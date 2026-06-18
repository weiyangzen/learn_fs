# sources/distributed-fs/ceph-client/include/linux/mlx5/mlx5_ifc_fpga.h

## Purpose
This header defines Mellanox mlx5 FPGA firmware interface layouts. It is a pure command/event ABI description: every `*_bits` structure is a bit-accurate mailbox, capability, or event record consumed by mlx5 command-building code via the generated `MLX5_GET`/`MLX5_SET` style accessors used throughout the driver. It has no executable control flow of its own.

## Important APIs, Types, And Data
- `struct mlx5_ifc_fpga_shell_caps_bits` and `struct mlx5_ifc_fpga_cap_bits` describe FPGA identity, firmware/image metadata, register access modes, DDR/control-register apertures, sandbox capabilities, and shell QP support.
- `MLX5_FPGA_CTRL_OPERATION_*` plus `struct mlx5_ifc_fpga_ctrl_bits` define control operations for image load, FPGA reset, flash selection, sandbox bypass, and sandbox reset.
- `struct mlx5_ifc_fpga_access_reg_bits` describes variable-size register access with `size`, 64-bit `address`, and flexible trailing byte data. `MLX5_FPGA_ACCESS_REG_SIZE_MAX` caps payloads at 64 bytes.
- `enum mlx5_ifc_fpga_qp_state`, `enum mlx5_ifc_fpga_qp_type`, and `enum mlx5_ifc_fpga_qp_service_type` define the FPGA QP state/type subset.
- `struct mlx5_ifc_fpga_qpc_bits` is the FPGA QP context. It carries state, QP type, traffic class, VLAN/PKey, PSNs, remote QPN, retry/RNR counters, remote/local MACs, and 16-byte IP addresses.
- Create, modify, query, counter-query, and destroy command input/output structures wrap `fpga_qpc` and expose `fpga_qpn`, `field_select`, `clear`, status, and syndrome fields.
- `struct mlx5_ifc_fpga_error_event_bits` and `struct mlx5_ifc_fpga_qp_error_event_bits` define asynchronous event payloads, including syndrome and failing FPGA QPN.

## Control Flow
Consumers query `mlx5_ifc_fpga_cap_bits` first to decide whether control/register/QP operations are legal, then build command mailboxes using the command-specific input structures. QP lifecycle follows create to query/modify to counter-query to destroy. Error handling is event-driven: the device reports one of the FPGA or FPGA-QP syndromes and upper layers map those values into driver log or recovery behavior.

## State And Persistence
State lives in device firmware, not in this header. Persistent or long-lived values include selected flash image, loaded image metadata, FPGA control state, sandbox bypass state, FPGA QP contexts, and QP counters. Kernel memory only holds encoded command buffers and decoded event/counter data.

## Dependencies And Integration Points
The file depends on common mlx5 IFC conventions: `u8 field[bits]` arrays, generated access macros, opcode values from other mlx5 command headers, and `mlx5_core_dev` command execution in the mlx5 core/FPGA code. The FPGA QP context overlaps semantically with RDMA/ethernet queue concepts but is a separate firmware ABI.

## Risks
The structures are bit-position sensitive; changing reserved field lengths or field order breaks firmware compatibility. Flexible register data must be bounded by `MLX5_FPGA_ACCESS_REG_SIZE_MAX`. QP fields combine network byte-order hardware values, PSNs, MACs, and IP arrays, so callers must populate them with the expected endianness and address family layout. Field-select masks for modify commands must match firmware-supported writable fields or modifications can silently fail with syndromes.

## Test Signals
Build coverage should compile mlx5 FPGA command users with these layouts. Runtime signals include successful FPGA capability queries, successful register access at boundary sizes 0 and 64, create/query/modify/destroy QP round trips, counter clear behavior, and injection or observation of each FPGA error event syndrome. ABI regression tests should check expected structure sizes and offsets when generated IFC tooling is available.
