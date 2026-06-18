# sources/distributed-fs/coda/coda-src/scripts/volsizes.pl

Purpose: Perl utility that compares sizes of replicated volume replicas using `/vice/db/VRList` and `/vice/vol/BigVolumeList`.

Control flow: reads VRList, pushes volume names into `@VOLUMENAMES`, then reads BigVolumeList, strips leading field markers, removes `.N` replica suffixes, records size for replica numbers 0, 1, and 2 when the base name matches a replicated volume, and finally prints a formatted overview marking rows with `*` when replica sizes differ.

State/persistence: read-only against fixed `/vice` files and process-local hashes for sizes.

Dependencies, risks, tests: depends on Perl, exact VRList/BigVolumeList formats, and at most first three replicas in output. Risks include a stray `shift` inside the VRList loop that mutates `@ARGV`, noisy "Adding" debug output, uninitialized-size comparisons, ignoring replicas 3-7, and hardcoded paths. Test with equal/different three-replica volumes, one/two/eight replicas, missing BigVolumeList, and names with dotted suffixes.
