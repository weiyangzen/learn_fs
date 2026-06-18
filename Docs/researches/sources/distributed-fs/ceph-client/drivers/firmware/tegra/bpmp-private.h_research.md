# sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp-private.h

Private operations contract between the Tegra BPMP core and SoC-specific transport implementations. `struct tegra_bpmp_ops` abstracts channel initialization/deinitialization, request/response readiness checks, request/response acknowledgements, free-channel checks, post operations, doorbell ringing, and optional resume handling.

The file declares `tegra186_bpmp_ops` and `tegra210_bpmp_ops`, letting `bpmp.c` select the correct implementation from SoC match data while keeping transfer and MRQ logic transport-agnostic. The operations take either `struct tegra_bpmp *` or `struct tegra_bpmp_channel *`, matching the public BPMP structures from `soc/tegra/bpmp.h`.

There is no runtime state here, but ABI stability matters inside the driver directory: every SoC implementation must provide semantics expected by `bpmp.c`, especially that post/ack/free/readiness operations are safe under the core locks and that `resume()` restores channel synchronization after noirq resume. Test signals include build coverage for each SoC guard, transfer tests through both op tables, and suspend/resume tests for SoCs with a resume callback.
