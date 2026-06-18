## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_ras.h

Purpose: Defines the Gen4 RAS register map, error source masks, per-block status/control masks, and the RAS ops initializer declaration.

Important APIs/types: The header enumerates ERRSOU0..3 source bits, AE correctable/uncorrectable log offsets, CPP command parity registers, RI/TI parity status and masks, SSM interrupt/status/control registers, SPP pull/push command/data parity registers, SER SSM shared-memory masks, CPP CFC registers, SSM compression/translator/decompression exception registers, ARAM ECC/memory target registers, ATU fault registers, and `adf_gen4_init_ras_ops()`.

Control flow/state: No state is stored, but these constants directly drive enable/disable and interrupt clear behavior in `adf_gen4_ras.c`. Several masks encode severity by grouping correctable, uncorrectable, and fatal bits.

Dependencies/integration: Included by Gen4 RAS implementation and tied to `adf_ras_ops` from common device data.

Risks and test signals: Header mask errors cause incorrect RAS behavior across the driver. Tests should compare masks with hardware documentation, compile all users, and verify each named mask through targeted fault injection or CSR mock tests.
