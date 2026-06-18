# sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/repository.c

Purpose: Provides the PS3 LV1 repository access layer. It encodes repository node names, reads PS3 platform inventory and partition metadata, locates devices/resources, exposes storage, memory, SPU, boot-data, VUART, BE, clock, and LPM privilege information, and optionally writes/deletes highmem region nodes.

Important APIs/types/functions: Defines PS3 vendor/LPAR constants and helpers `make_first_field()`, `make_field()`, and `read_node()`. Public readers include bus/device functions, `ps3_repository_find_device()`, `ps3_repository_find_device_by_id()`, `ps3_repository_find_devices()`, `ps3_repository_find_bus()`, `ps3_repository_find_interrupt()`, `ps3_repository_find_reg()`, storage-region readers, memory readers, SPU reservation readers, boot-data/VUART readers, BE/timebase readers, and `ps3_repository_read_lpm_privileges()`. Under `CONFIG_PS3_REPOSITORY_WRITE`, highmem write/delete helpers wrap LV1 create/write/delete calls.

Control flow: All normal reads flow through `read_node()`, which resolves the current LPAR id when requested, calls `lv1_read_repository_node()`, converts LV1 failure into `-ENOENT`, and copies up to two 64-bit values to callers. Higher-level helpers build fixed node paths such as `bus/dev/reg/data`, iterate bounded bus/device/resource indexes, and stop on not-found conditions. Compound readers call lower-level readers in sequence and return the first error.

State and persistence: The file keeps no global mutable runtime cache; repository contents live in the PS3 hypervisor. The write path persists highmem metadata into repository nodes when enabled. Temporary state is stack-local `ps3_repository_device` snapshots and read values. Debug dumping is compiled only under `DEBUG`.

Dependencies and integration points: Depends on `asm/lv1call.h`, `platform.h`, PS3 repository naming conventions, PS3 system bus discovery, memory setup, SPU setup, storage drivers, VUART/system-manager setup, and time calibration. It is an integration boundary between Linux platform code and LV1 repository services.

Risks: Hard-coded search bounds of 10 buses/devices/resources can miss firmware layouts outside assumptions. Many readers assign output values even when the read failed, so callers must honor return codes. Node-field encoding depends on endian/layout details of copied strings. Optional write support can leave partially updated highmem metadata if only one of the base/size writes or deletes succeeds.

Test signals: Useful signals include PS3 boot logs with repository reads, successful discovery of storage/network/USB/GPU/VUART devices, SPU resource enumeration, timebase calibration from BE data, highmem region import/export, `DEBUG` repository dumps, and fault-injection of LV1 `NO_ENTRY` paths.

Source read size: 1380 lines, 32930 bytes.
