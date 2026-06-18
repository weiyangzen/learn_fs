# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc.h

## Purpose

This header defines the HuC object shape and public lifecycle/authentication API. It connects generic uC firmware management with HuC-specific status registers, delayed GSC/PXP loading, and GSCCS authentication packet storage.

## Important APIs, Types, And Functions

`enum intel_huc_delayed_load_status` distinguishes waiting on GSC, waiting on PXP, and delayed-load error. `enum intel_huc_authentication_type` defines GuC and GSC auth slots. `struct intel_huc` embeds `struct intel_uc_fw`, per-auth status register/mask/value triplets, delayed-load fence/timer/notifier/status, optional `heci_pkt`, and `loaded_via_gsc`.

The inline helpers expose supported/wanted/used state through generic firmware status, identify GSC-load mode, and tell callers whether submissions must wait for GSC authentication.

## Control Flow, Dependencies, Risks, And Test Signals

`intel_uc.h` embeds this structure in `struct intel_uc`; `intel_huc.c`, `intel_huc_fw.c`, and debugfs consume the declarations. The main contract risk is that `intel_huc_is_used()` asserts the firmware has moved past transient selected state, so callers must run fetch/init in order. `intel_huc_wait_required()` can stall userspace submission until delayed GSC authentication finishes, so fence completion paths and status updates are critical. Build coverage, HuC status getparam, debugfs, and delayed-load tests are the key signals.
