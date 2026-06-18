# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-4-7.c

## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-4-7.c

Purpose: Implements CSID operations for the 4.7-generation block, similar to 4.1 but with updated register offsets and optional packed 10-bit output conversion for selected source-pad formats.

Important APIs/types/functions: Exports `csid_ops_4_7`. Uses `csid_configure_stream()`, `csid_configure_testgen_pattern()`, `csid_isr()`, `csid_reset()`, and `csid_subdev_init()`.

Control flow/state: Enable configures testgen or sensor RX, writes CID LUT and CID config, and starts TG if enabled. It checks sink/source codes for SBGGR10 or Y10 converted to `*_2X8_PADHI_LE`; in that case it sets RDI plain-packing mode, plain16 format, and LSB alignment. Reset and ISR mirror the Gen1 completion model with 4.7 offsets.

Dependencies/integration: Common CSID code supplies active formats, test pattern control, media-link lane data, and power sequencing. VFE/ISPIF downstream consumes the configured RDI/ISPIF path.

Risks/test signals: Key risks are packed-format matching and source-code negotiation in `csid_src_pad_code()`. Test raw10 unpacked vs packed paths, testgen operation, VC0 assumptions, reset IRQ completion, and link validation with 4.7 format tables.
