# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/iostat-10s

Symlink to `iostat`; behavior is selected by invoked basename `iostat-10s`.

Behavior:
- Uses the same vdev path resolution and output parsing as `iostat`.
- Sets interval to 10 seconds and suppresses summary stats where supported.
- Collects one 10-second sample and prints parsed metrics as `column=value`.
- Produces no output for file-based vdevs.

Role:
- Provides sampled 10-second per-vdev iostat custom columns.
