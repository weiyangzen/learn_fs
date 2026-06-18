# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-340.c

## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-340.c

Purpose: Implements CSID hardware operations for the Qualcomm 340-generation CSI decoder, focused on RDI raw dump paths without CSID test-generator support.

Important APIs/types/functions: Provides `csid_ops_340`. Helpers configure RX lane/PHY selection, RDI stream format, RDI halt/resume, reset, and IRQ handling. It uses Gen2 decode definitions and common helpers `csid_get_fmt_entry()`, `csid_hw_version()`, and `csid_src_pad_code()`.

Control flow/state: `csid_configure_stream()` programs CSI2 RX registers and loops over enabled virtual channels in `csid->phy.en_vc`, configuring one RDI per VC. RDI config uses data type, VC, and derived `dt_id`, sets decode format to NOP/raw dump, then enables the RDI if requested. Reset masks/clears reset-done IRQ, strobe-resets IRQ/IFE/PHY/CSID clocks while preserving registers, waits on `reset_complete`, and ISR completes that completion on reset IRQ.

Dependencies/integration: Plugged into the common CSID core via `struct csid_hw_ops`; depends on CAMSS media-link setup to fill `csid->phy`, and on VFE/IFE downstream blocks for actual buffer handling.

Risks/test signals: No testgen means sensor path must be linked. Verify reset completion, lane assignment/PHY base index, multi-VC RDI mapping, stream disable clearing RDI enable, and unsupported test pattern returning `-EOPNOTSUPP`.
