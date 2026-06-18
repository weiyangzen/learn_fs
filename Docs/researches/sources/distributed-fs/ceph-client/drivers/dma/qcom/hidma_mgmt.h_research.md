# sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_mgmt.h

Purpose: shared header for HIDMA management common-register and sysfs code. It defines `struct hidma_mgmt_dev` and prototypes the setup/sysfs entry points.

Important APIs/types/functions: `struct hidma_mgmt_dev` stores hardware revision, max transaction/request limits, channel count, reset timeout, per-channel priority and weight arrays, mapped register base/size, sysfs channel kobject roots, and owning platform device. `hidma_mgmt_setup` programs validated state to hardware; `hidma_mgmt_init_sys` creates sysfs controls.

Control flow: `hidma_mgmt.c` allocates and populates this structure at probe, calls setup, then passes it to `hidma_mgmt_sys.c`. Sysfs writes mutate fields and call setup to reprogram hardware.

State/persistence: all fields are runtime management state mirrored into MMIO; no persistent storage is present. `chroots` is allocated per channel for sysfs hierarchy.

Dependencies/integration: relies on platform device lifetime and MMIO access from implementation files. It intentionally has no include guard in the shown file, so double-inclusion risks should be considered if includes expand.

Risks: because sysfs and setup share the same mutable structure without explicit locking in this header contract, concurrent writes could interleave unless higher-level sysfs serialization is sufficient for the intended use. Adding fields requires updating both property parsing and sysfs.

Test signals: compile both management objects, probe with several `dma-channels` values, inspect sysfs channel tree, and verify register updates after sysfs writes.
