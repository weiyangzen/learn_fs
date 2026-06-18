# sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp-tegra186.c

Tegra186-and-newer BPMP transport implementation. It uses HSP mailbox notifications plus Tegra IVC queues in SRAM or reserved DRAM to implement the private BPMP operation table consumed by `bpmp.c`.

`struct tegra186_bpmp` stores the parent BPMP pointer, TX/RX shared-memory backing with optional genpools, physical addresses, and a mailbox client/channel. Readiness and free checks are direct wrappers around `tegra_ivc_read_get_next_frame()` and `tegra_ivc_write_get_next_frame()`, setting `channel->ib` or `channel->ob`. Ack/post operations advance IVC read/write counters. `tegra186_bpmp_ring_doorbell()` sends an HSP mailbox message and marks TX done.

Channel setup first tries a reserved-memory region: first 4 KiB for TX and second 4 KiB for RX. If no reserved memory exists, it allocates two `"shmem"` genpool regions. Each BPMP channel gets a one-frame IVC queue using `MSG_MIN_SZ` aligned to 64 bytes and offset by channel index. Init requests the HSP mailbox, resets all channels through the IVC state machine, and installs the mailbox RX callback that calls `tegra_bpmp_handle_rx()`.

State persists in shared memory and BPMP firmware; Linux stores mapped queue pointers, genpool allocations, channel completions, and mailbox handle. Resume resets IVC channels to reestablish synchronization after suspend. Dependencies include `tegra_ivc`, mailbox client API, reserved-memory parsing, genalloc SRAM pools, BPMP ABI message sizing, and the private op contract.

Risks include hard-coded 4 KiB TX/RX windows: channel count, frame size, and ABI changes must continue to fit. `tegra186_bpmp_channel_reset()` busy-waits until `tegra_ivc_notified()` succeeds, so broken firmware synchronization can spin. DRAM init maps the full reserved region for TX and uses an offset pointer for RX, while size validation only requires at least 8 KiB. Test signals include reserved-memory and SRAM fallback probe paths, HSP mailbox request failure, IVC reset convergence, suspend/resume transfer recovery, and MRQ traffic on all threaded channel indexes.
