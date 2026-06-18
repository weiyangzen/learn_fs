# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-4-1.c

## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-4-1.c

Purpose: Implements CSID hardware operations for older 4.1-generation Qualcomm CAMSS blocks, including sensor RX configuration, CID LUT programming, RDI/ISPIF enablement, and an internal test generator.

Important APIs/types/functions: Exports `csid_ops_4_1`. `csid_configure_stream()` handles both testgen and real sensor paths. `csid_configure_testgen_pattern()` stores the selected payload mode. `csid_isr()` handles reset completion from IRQ status bit 11. `csid_reset()` issues reset and waits for `reset_complete`. `csid_subdev_init()` enables Gen1 test pattern modes.

Control flow/state: On enable, if testgen is active the source format drives bytes-per-line, line count, data type, and payload mode registers; otherwise sink format and `csid->phy` program core lane and PHY controls. Both paths populate VC0/CID0 LUT and CID config with ISPIF and RDI enabled and raw-dump mode, then enable TG if applicable. Disable only turns off TG when active.

Dependencies/integration: Used by common `camss-csid.c` power, format, control, and media-link code. Uses Gen1 decode constants and `csid_testgen_modes`.

Risks/test signals: It assumes VC0/CID0 only and lacks multi-source-pad RDI handling. Test reset timeout, test-pattern exclusive use vs linked CSIPHY, format byte-count calculations, sensor streaming with lane assignment, and source format propagation.
