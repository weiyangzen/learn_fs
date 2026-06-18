<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hex.h -->
# sources/distributed-fs/ceph-client/include/linux/hex.h

Purpose: This header declares common hex conversion helpers.

Important APIs/types/functions: It exposes hex character tables, `hex_to_bin()`, `hex2bin()`, `bin2hex()`, `hex_dump_to_buffer()`, `print_hex_dump()`, `print_hex_dump_bytes()`, and related row/group/prefix constants. These helpers convert ASCII hex to bytes, bytes to ASCII hex, and binary buffers to formatted diagnostic output.

Control flow, state, and persistence: Conversion helpers are stateless. `hex2bin()` validates pairs of hex characters and returns an error for invalid input. Dump helpers format rows with configurable row size, group size, ASCII inclusion, and prefix style before printing or returning text.

Dependencies/integration: It integrates with kernel logging/printk and is used widely by protocol, driver, crypto, and debug paths.

Risks and test signals: Invalid hex input, odd lengths, insufficient output buffers, and formatting expectations are the main concerns. Tests should cover upper/lowercase digits, invalid characters, zero-length buffers, every grouping mode, ASCII column formatting, prefix address/offset modes, and output truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hex.h -->
