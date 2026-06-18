# sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_spi.c

## Purpose

`scsi_transport_spi.c` implements the SCSI Parallel Interface transport class. It exposes per-host and per-target SPI negotiation attributes through sysfs, derives target capabilities from inquiry data, performs SPI domain validation, formats transfer agreements, builds negotiation/tag messages for LLDDs, and optionally decodes SCSI message bytes for logging.

The file serves legacy parallel SCSI HBAs that attach with `spi_attach_transport()` and provide a `struct spi_function_template` for reading and setting bus negotiation parameters.

## Important APIs, Types, and Functions

`struct spi_internal` wraps a `struct scsi_transport_template` and the LLDD `struct spi_function_template`. Target state lives in `struct spi_transport_attrs` stored in `scsi_target->starget_data`; host state lives in `struct spi_host_attrs` stored in transport host data.

Public transport lifecycle APIs are `spi_attach_transport()` and `spi_release_transport()`. Domain validation APIs are `spi_dv_device()` and `spi_schedule_dv_device()`. Negotiation/logging helpers are `spi_display_xfer_agreement()`, `spi_populate_width_msg()`, `spi_populate_sync_msg()`, `spi_populate_ppr_msg()`, `spi_populate_tag_msg()`, and `spi_print_msg()`.

Important internal functions include `spi_device_configure()` for inquiry-derived capabilities, `spi_setup_transport_attrs()` for default target negotiation state, `target_attribute_is_visible()` for sysfs visibility and writability, `spi_dv_device_internal()` for the validation algorithm, `spi_dv_retrain()` for fallback negotiation, and echo/inquiry compare helpers for validation tests.

## Control Flow

Module initialization registers an SPI-specific SCSI device-info list, seeds a small blacklist that disables Information Units on known tape models, registers the target transport class, registers an anonymous SCSI-device class used for device configuration, and registers the host class. Exit unregisters classes and removes the device-info list.

Attaching a transport allocates `struct spi_internal`, registers target and host containers, sets target and host private data sizes, and stores the driver callback table. The host setup path initializes signalling to unknown. Host configure makes the `signalling` sysfs attribute writable only if the driver has `set_signalling()`.

When a SCSI device is configured, the anonymous device class reads inquiry-derived capabilities: sync, wide, double-transition, DT-only, Information Units, and QAS. The SPI blacklist can force IU support off. Target setup initializes conservative transfer state: invalid period, async offset, narrow width, IU/QAS disabled but max-capable, validation flags clear, and a mutex for domain validation.

Target sysfs attributes are visible only if both the target capability and driver callbacks support them. Period, offset, width, IU, DT, QAS, flow-control, stream, RTI, precompensation, and hold-MCS settings read through optional driver getters and write through driver setters. Max attributes clamp writes to cached maximums. `revalidate` triggers domain validation on the first child SCSI device.

Domain validation can run synchronously with `spi_dv_device()` or asynchronously with `spi_schedule_dv_device()`. The synchronous path blocks suspend/resume with `lock_system_sleep()`, takes runtime-PM and SCSI-device references, prevents duplicate validation with `dv_in_progress`, allocates a double echo buffer, quiesces the device and target, sets `dv_pending`, takes the target DV mutex, runs `spi_dv_device_internal()`, then resumes and clears state.

The validation algorithm starts at narrow asynchronous transfer and verifies stable inquiry reads. It attempts wide transfer if supported, disables wide if inquiry comparison fails, then negotiates the fastest allowed synchronous/DT settings: max offset, minimum period, optional QAS, IU and IU-related options for fast periods, DT based on bus signalling and target support, and width last. It validates with repeated inquiry reads, reads the actual DT state, optionally discovers an echo buffer, and if present performs write/read pattern tests. On failures, `spi_dv_retrain()` disables IU, then QAS, then backs off the transfer period until validation succeeds or falls back to asynchronous mode.

## State and Persistence Behavior

State is volatile. Per-target fields cache current and maximum negotiation values, capability-derived support bits, DV pending/in-progress flags, and whether initial DV completed. Per-host state caches the SPI signalling mode. There is no persistent store; all settings are rebuilt from driver callbacks, inquiry data, sysfs writes, and domain validation for the life of the SCSI target/host.

DV state has two layers: `spi_dv_pending()` prevents scheduling duplicate work, and `spi_dv_in_progress()` prevents concurrent synchronous validation. The target DV mutex serializes the actual validation body. SCSI runtime-PM references, device references, quiesce/resume, and system sleep locking protect against validation during suspend/resume or device teardown.

## Dependencies and Integration Points

The file depends on the SCSI midlayer, transport classes, SCSI inquiry capability helpers, SCSI device-info blacklist infrastructure, SCSI command execution, runtime PM, system sleep locking, workqueues, target quiesce/resume, tagged-queue helpers, and optional SCSI constants for message decoding.

LLDDs provide `get_*` and `set_*` callbacks for SPI negotiation fields, signalling callbacks, optional `deny_binding()` to suppress transport binding for targets, and callback behavior for actual hardware negotiation. The exported message builders are used by drivers when constructing WDTR, SDTR, PPR, and tag messages.

## Risks and Edge Cases

Domain validation is intrusive: it issues commands, quiesces devices, changes negotiation parameters, and falls back on errors. Incorrect driver setters or devices that misreport echo-buffer support can cause unnecessary speed downgrades; the code handles one known class by skipping write tests on invalid-field WRITE BUFFER responses.

Capability visibility is dynamic. Sysfs attributes appear only when target support and callbacks align, and `spi_target_configure()` forces group updates after capabilities are populated. Drivers that update support bits later must ensure sysfs visibility remains coherent.

Several store paths parse numbers with `simple_strtoul()` and minimal validation. Invalid trailing characters are not rejected for simple numeric attributes. Period parsing accepts fractional nanoseconds but rounds into PPR or SDTR period fields and clamps only high values or minimum-period requirements.

The asynchronous DV wrapper clears `dv_pending` after `spi_dv_device()` also manipulates pending state. The ordering is intentional but depends on the SCSI device reference and work item lifetime being correct.

The transfer-rate display and period conversion tables cover defined PPR periods and then fall back to period * 4 ns. Reserved or future encodings can display as `FAST-?` or `reserved`.

## Test Signals

Useful signals include module init adding and removing the SPI device-info list; host sysfs attributes for signalling, width, and HBA ID; target attributes appearing only for supported capabilities and callbacks; blacklist behavior disabling IU for matching inquiry strings; sysfs writes clamping max offset/width/IU/QAS and minimum period; manual `revalidate` triggering DV; DV fallback from IU to QAS to slower periods to async; echo-buffer discovery and skip handling; runtime-PM and suspend/resume exclusion during DV; formatted transfer agreement logs for async, narrow/wide, ST/DT, and IU/QAS options; and correctness of WDTR, SDTR, PPR, queue tag, and message printing helpers.
