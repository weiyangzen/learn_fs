<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_imx8q.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_imx8q.c

Purpose: implements i.MX8Q platform-specific setup, reset, firmware boot customization, memory-region classification, system-config population, and optional SCU fuse checks for codec availability.

Important APIs/functions: `vpu_imx8q_setup()`, `vpu_imx8q_setup_dec()`, `vpu_imx8q_setup_enc()`, `vpu_imx8q_reset()`, `vpu_imx8q_set_system_cfg_common()`, `vpu_imx8q_boot_core()`, `vpu_imx8q_get_power_state()`, `vpu_imx8q_on_firmware_loaded()`, `vpu_imx8q_check_memory_region()`, `vpu_imx8q_check_codec()`, and `vpu_imx8q_check_fmt()`.

Control flow: parent/core setup writes SoC block-control registers to enable clocks and release resets. Firmware boot writes the firmware physical address to CM0P CSR and clears CPUWAIT. Firmware-loaded hook patches platform type, core ID, and a flag into the firmware image. System config maps core IDs to Malone or Windsor register bases and IRQ pins. With `CONFIG_IMX_SCU`, fuse values are fetched once from SCU and used to disable whole codecs or specific H.264/HEVC decoder formats.

State and persistence: optional static `imx8q_fuse` and `fuse_got` cache SCU fuse state for the module lifetime. Hardware register state persists in the device until reset/power changes.

Dependencies and integration: used by parent resource callbacks and iface ops in `vpu_rpc.c`; depends on i.MX SCU firmware APIs when configured and register offsets from `vpu_imx8q.h`.

Risks: setup/reset sequences are SoC-specific and largely unchecked. `vpu_imx8q_check_memory_region()` requires `addr + size < region->end`, excluding exact-end regions. Firmware image patching assumes at least 19 bytes. Fuse failure returns permissive defaults in non-SCU or read-failure paths.

Test signals: boot both encoder and decoder cores, verify CSR CPUWAIT transitions, validate system config addresses for core IDs 0/1/2, run with SCU fuse configurations disabling encoder/H.264/HEVC, and test reserved memory at region boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_imx8q.c -->
