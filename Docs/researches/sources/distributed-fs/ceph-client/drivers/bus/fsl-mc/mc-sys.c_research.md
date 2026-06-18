# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/mc-sys.c

Purpose: low-level command transport for FSL MC portals. It writes command parameters/header to portal MMIO, polls for firmware completion, reads responses, maps MC firmware statuses to Linux errors, and serializes each portal.

Important APIs: exported `mc_send_command()` is the main entry point. `mc_cmd_hdr_read_cmdid()` exposes command ID decoding. Internal helpers read status, translate status/error strings, perform endian-aware `writeq`/`readq` portal access, and implement preemptible versus atomic polling.

Control flow: callers fill `struct fsl_mc_command`. `mc_send_command()` rejects hardirq use on non-atomic portals, locks the portal, writes params first and header last, then polls until status is no longer READY or timeout. Non-atomic portals use `usleep_range()`; atomic portals use `udelay()` under raw spinlock. On OK status, response params are copied into the command. On error, MC status maps to errno.

State and persistence: state is limited to the caller's command buffer and portal lock. MC firmware state changes happen as side effects of commands; this file does not retain them.

Dependencies and integration: depends on `struct fsl_mc_io` locking mode, MMIO helpers, command header layout from public/private MC headers, jiffies timing, and kernel errno conventions. It underpins bus probe, DPRC scans, MSI programming, object APIs, and UAPI.

Risks: command completion timeout is 15 seconds; atomic portals busy-wait for the whole timeout budget. Endian handling intentionally compensates for IO accessors, so changing it is high risk. Missing command completion interrupts are noted as a TODO. Test signals include successful/failed MC commands, status-to-errno mapping, timeout path, hardirq rejection for sleeping portals, concurrent command serialization, and response endian correctness.
