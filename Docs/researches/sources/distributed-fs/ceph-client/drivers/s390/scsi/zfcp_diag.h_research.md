# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_diag.h`

## Purpose

`zfcp_diag.h` declares the diagnostic cache structures and public diagnostic update API for the zfcp driver. It defines the common metadata header used to protect and age diagnostic buffers, the adapter-level container for exchange-port/config data, and a feature predicate for SFP reporting support.

## Important APIs, Types, And Data

- `struct zfcp_diag_header` is the common diagnostic-buffer header:
  - `access_lock` protects all metadata and buffer contents.
  - Bitfields `updating` and `incomplete` track an active producer and partial data.
  - `timestamp` stores the last capture time in jiffies.
  - `buffer` and `buffer_size` point to the implementation-specific payload.
- `struct zfcp_diag_adapter` stores:
  - `max_age`, the freshness window in milliseconds.
  - `port_data.header` plus cached `struct fsf_qtcb_bottom_port`.
  - `config_data.header` plus cached `struct fsf_qtcb_bottom_config`.
- `zfcp_diag_adapter_setup()` and `zfcp_diag_adapter_free()` manage per-adapter diagnostic storage.
- `zfcp_diag_update_xdata()` publishes a diagnostic payload into a header.
- `typedef zfcp_diag_update_buffer_func` defines the synchronous refresh callback shape.
- `zfcp_diag_update_config_data_buffer()` and `zfcp_diag_update_port_data_buffer()` are concrete refresh callbacks.
- `zfcp_diag_update_buffer_limited()` is the public rate-limited refresh coordinator.
- `zfcp_diag_support_sfp()` returns true when `adapter->adapter_features` includes `FSF_FEATURE_REPORT_SFP_DATA`.

## Control Flow And Integration

Consumers use the header in two layers. General code calls the rate-limited update coordinator with one of the concrete update callbacks. FSF exchange handlers use `zfcp_diag_update_xdata()` to publish returned QTCB-bottom data. The cached buffers are the same FSF data structures used by SCSI host update and sysfs diagnostics, so this header is a bridge between hardware exchange commands and user-visible diagnostic attributes.

## State And Persistence

The header describes per-adapter in-memory caches only. The buffer pointer points at embedded storage in `struct zfcp_diag_adapter`; it is not separately allocated. The incomplete flag persists until a later successful publish updates the header. `max_age` persists for the adapter lifetime and can be used by all diagnostic readers.

## Dependencies

The header includes Linux spinlocks, `zfcp_fsf.h` for QTCB-bottom and feature constants, and `zfcp_def.h` for the adapter declaration. Because `zfcp_def.h` also contains a diagnostics pointer, include-order coupling matters.

## Risks And Edge Cases

- `updating` and `incomplete` are `u64` bitfields. Code must mutate them under `access_lock`; bitfield layout should not be exposed externally.
- `buffer` is a raw `void *`; publishers must provide data matching `buffer_size` and the intended payload type.
- `zfcp_diag_support_sfp()` depends on adapter features already being populated by exchange-config-data.
- Adding new diagnostic buffers should follow the same embedded-data plus header pattern to avoid lifetime mismatches.

## Test Signals

Look for:

- Correct header initialization for both config and port buffers.
- SFP sysfs/reporting paths disabled until `FSF_FEATURE_REPORT_SFP_DATA` appears.
- Diagnostic readers hold or coordinate on `access_lock` while copying data.
- Incomplete flag is visible after incomplete exchange data and clears after complete data.
