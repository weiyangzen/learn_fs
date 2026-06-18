# sources/distributed-fs/ceph-client/include/soc/tegra/bpmp.h

## Purpose

`bpmp.h` is the Linux kernel client interface for Tegra BPMP firmware. It turns the wire ABI from `bpmp-abi.h` into device, mailbox, IVC, reset, clock, power-domain, and debugfs-facing types and APIs.

## Important APIs, Types, and Functions

`struct tegra_bpmp_soc` describes SoC channel geometry and operations. `struct tegra_bpmp_mb_data` is the mailbox frame with `code`, `flags`, and `data[MSG_DATA_MIN_SZ]`; the `tegra_bpmp_mb_*` macros copy fields through `iosys_map`. `struct tegra_bpmp_channel` tracks input/output maps, completion, optional IVC channel, and index. `struct tegra_bpmp` holds the device, mailbox client/channel, atomic TX lock, TX/RX/threaded channels, threaded-channel allocation state, inbound MRQ handlers, clocks, reset controller, genpd data, optional debugfs mirror, and suspend flag.

Public calls include `tegra_bpmp_get()`, `tegra_bpmp_get_with_id()`, `tegra_bpmp_put()`, `tegra_bpmp_transfer_atomic()`, `tegra_bpmp_transfer()`, `tegra_bpmp_mrq_return()`, `tegra_bpmp_request_mrq()`, `tegra_bpmp_free_mrq()`, and `tegra_bpmp_mrq_is_supported()`. Provider initializers cover clocks, resets, powergates, and debugfs behind config guards.

## Control Flow

A consumer obtains a BPMP handle, fills `struct tegra_bpmp_message` with MRQ ID and TX/RX buffers, sends it through the atomic or sleeping transfer path, and receives response data and return status. BPMP-originated MRQs are matched against the registered `struct tegra_bpmp_mrq` list and answered with `tegra_bpmp_mrq_return()`.

## State and Persistence

Runtime state lives in `struct tegra_bpmp`: channel allocation, busy bitmaps, MRQ callback list, provider state, and suspend state. The header itself persists nothing, but exposes synchronization-sensitive state shared by BPMP transport and provider drivers.

## Dependencies and Integration Points

The header depends on Linux `iosys-map`, mailbox, PM domain, reset-controller, semaphores, locks, lists, device infrastructure, and `soc/tegra/bpmp-abi.h`. It integrates with Tegra clock, reset, power-domain, debugfs, mailbox, and IVC implementations. Disabled configs compile through `-ENODEV` and `false` stubs.

## Risks

Risks include payload-size mismatches, using sleeping transfer from atomic context, channel allocation races, lost completions, stale MRQ handlers after teardown, and optional-provider init order issues.

## Test Signals

Test enabled and disabled configs, ping/query ABI transfers, atomic and threaded transfer paths, MRQ handler registration/freeing, inbound MRQ replies, suspend behavior, and optional clock/reset/powergate/debugfs initialization.
