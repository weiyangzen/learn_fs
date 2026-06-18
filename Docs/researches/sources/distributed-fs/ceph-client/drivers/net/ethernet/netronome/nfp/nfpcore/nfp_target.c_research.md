# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_target.c

Purpose: Encodes hardware knowledge for CPP target/action push-pull widths and translates island CPP IDs/addresses into target CPP IDs/addresses using IMB address-mode tables.

Important APIs/types/functions: `nfp_target_pushpull()` returns encoded read/write widths for NBI, QDR, ILA, MU, PCIe, ARM, crypto, CT XPB, CLS, and target 0. `nfp_target_cpp()` translates island IDs through `nfp_cppat_addr_encode()`. Helpers implement basic target and MU address encoding for IMB modes 0-3.

Control flow: Width decoding switches on target and action/token combinations, returning 32-bit, 64-bit, read-only, write-only, or invalid encodings used by PCIe area setup. Address translation leaves island 0 unchanged; otherwise it reads the target's IMB mode/address width/island fields and rewrites address bits so target-level CPP access reaches the requested island.

State and persistence: Stateless pure translation logic. It consumes the IMB table snapshot stored in `struct nfp_cpp`.

Dependencies/integration: Used by `nfp_cpp_area_alloc_with_name()` before backend area init and by `nfp6000_pcie.c` to determine access width. Depends on NFP6000 target constants and MU locality helper semantics.

Risks: Incorrect address bit encoding routes transactions to wrong islands. QDR and MU special cases intentionally reject or only validate some encodings. Unsupported target/action pairs return `-EINVAL`, which can make higher-level accesses fail at area allocation.

Test signals: Unit-style tests for each target/action width, island 0 passthrough, IMB mode 0-3 translation, MU direct/locality cases, CT XPB constraints, and invalid target/action rejection.
