# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/iostat-1s

Symlink to `iostat`; behavior is selected by invoked basename `iostat-1s`.

Behavior:
- Uses the same vdev path resolution and output parsing as `iostat`.
- Sets interval to 1 second and suppresses summary stats where supported.
- Collects one 1-second sample and prints parsed metrics as `column=value`.
- Produces no output for file-based vdevs.

Role:
- Provides sampled 1-second per-vdev iostat custom columns.
