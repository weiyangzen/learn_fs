# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_dev.h

Purpose: Declares supported Netronome/Corigine PCI IDs, the internal `enum nfp_dev_id`, and `struct nfp_dev_info` consumed by probe and low-level transport code.

Important APIs/types/functions: Defines `PCI_VENDOR_ID_CORIGINE`, PF/VF device IDs for NFP3800/NFP4000/NFP5000/NFP6000, `enum nfp_dev_id`, and `extern const struct nfp_dev_info nfp_dev_info[]`.

Control flow/state: Header-only constants and type declarations. Runtime behavior comes from table consumers.

Dependencies/integration: Included by `nfp_dev.c`, PCI probe code, and `nfp6000_pcie.c`.

Risks: Device ID or enum/table order mismatch can select wrong chip parameters. PF-only fields must be treated as unavailable for VF entries.

Test signals: PCI ID table compile/link checks and probe tests confirming the correct `nfp_dev_info` index for each device ID.
