## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_hw_data.c

Purpose: Implements Gen2 hardware helper operations for accelerator counts, error correction, IOV thread mapping, admin/arbiter info, interrupts, capability discovery, watchdog timers, and compression request templates.

Important APIs/functions: Exported helpers include `adf_gen2_get_num_accels()`, `adf_gen2_get_num_aes()`, `adf_gen2_enable_error_correction()`, `adf_gen2_cfg_iov_thds()`, `adf_gen2_get_admin_info()`, `adf_gen2_get_arb_info()`, `adf_gen2_enable_ints()`, `adf_gen2_get_accel_cap()`, `adf_gen2_set_ssm_wdtimer()`, and `adf_gen2_init_dc_ops()`. Compression ops build Gen2 firmware config words for DEFLATE compression/decompression only.

Control flow and state: The file programs PMISC CSRs to enable AE ECC, SSM shared-memory errors, AE-to-function valid bits, interrupt masks, and watchdog timers. Capability state is computed from PCI `LEGFUSE`, straps, and fuses and returned as a mask; it is not persisted here. DC ops are stored in an ops table supplied by the caller.

Dependencies/integration: Depends on PCI config reads, QAT firmware compression structs, admin/arbiter consumers, IOV setup, and Gen2 register macros from the header.

Risks and test signals: The capability mask must match fused-off slices and power-gated PKE/DC. IOV thread valid-bit toggling can affect SR-IOV isolation. Tests should validate fuse/strap combinations, interrupt masks with/without VFs, watchdog CSR writes for each accelerator, and that unsupported compression algorithms return `-EINVAL`.
