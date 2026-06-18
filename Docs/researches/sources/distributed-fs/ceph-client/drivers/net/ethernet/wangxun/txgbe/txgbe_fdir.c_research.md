# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_fdir.c

## Purpose
`txgbe_fdir.c` implements TXGBE Flow Director support. It computes ATR signature and perfect-filter hashes, samples TCP transmit flows for signature filters, programs input masks and perfect filters, erases filters, initializes Flow Director hardware, restores software rules after reconfiguration, and frees rule state.

## Important APIs, Types, and Functions
Exports are `txgbe_atr_compute_perfect_hash()`, `txgbe_atr()`, `txgbe_fdir_set_input_mask()`, `txgbe_fdir_write_perfect_filter()`, `txgbe_fdir_erase_perfect_filter()`, `txgbe_configure_fdir()`, and `txgbe_fdir_filter_exit()`. Internal helpers include `txgbe_atr_compute_sig_hash()`, `txgbe_fdir_check_cmd_complete()`, `txgbe_fdir_add_signature_filter()`, `txgbe_fdir_enable()`, `txgbe_init_fdir_signature()`, `txgbe_init_fdir_perfect()`, and `txgbe_fdir_filter_restore()`.

## Control Flow
TX ATR sampling runs from transmit context: it decodes packet type, accepts TCP IPv4/IPv6 outer or tunnel flows, skips FIN packets, samples SYN or every configured interval, builds inverted receive-side input/common hash dwords, and programs a signature filter to the queue associated with the interrupt vector. Perfect-filter ethtool paths compute masks and hashes before calling `txgbe_fdir_write_perfect_filter()`. Driver configuration disables the secure RX path, initializes either signature or perfect mode, restores saved perfect rules, then re-enables secure RX.

## State and Persistence Behavior
Hardware state includes Flow Director hash keys, control registers, input mask registers, flex-byte config, hash/cmd registers, and programmed filters. Software state for perfect rules lives in `struct txgbe` and is freed on close through `txgbe_fdir_filter_exit()`. Signature ATR rules are generated dynamically and not stored as per-rule software state.

## Dependencies and Integration Points
The file depends on packet type decoding from `wx_type.h`, TX ring/buffer state, Flow Director register definitions from `txgbe_type.h`, secure RX path helpers, ethtool rule management, and transmit fast path callback `wx->atr` installed by `txgbe_sw_init()`.

## Risks and Edge Cases
IPv6 perfect masking is explicitly unsupported. Command completion polling uses a 100 microsecond total timeout, so slow hardware can produce errors. ATR assumes TX and RX queues are CPU-paired. Perfect filter restore skips rules whose target ring is now out of range. Mask validation is strict and hardware supports only one mask per port.

## Test Signals
Test ATR insertion for TCP IPv4/IPv6, tunnel and non-tunnel packets, SYN and sample-rate paths, and FIN skip. Test perfect filter add/delete/restore, mask validation, queue/drop actions, command timeout injection, secure RX path disable/enable, and ring-count changes with existing filters.
