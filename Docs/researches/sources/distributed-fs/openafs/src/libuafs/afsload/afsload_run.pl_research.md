## sources/distributed-fs/openafs/src/libuafs/afsload/afsload_run.pl

Purpose: Runtime MPI harness for afsload. Rank 0 acts as the director and Test::More reporter; all other ranks initialize `AFS::ukernel` and execute configured filesystem actions.

Important logic: Uses `Parallel::MPI::Simple`, `AFS::Load::Config`, and on worker ranks `AFS::ukernel`. Maintains `@steps` and `%nodeconf`, where default logfile is `/dev/null` and default AFS config uses a rank-specific cache directory.

Control flow: Initializes MPI, loads the config using `rank-1` because user node 0 maps to MPI rank 1, validates at least one step, and initializes Test::More on rank 0. Worker ranks redirect stdout/stderr, call `uafs_Setup`, `uafs_ParseArgs`, and `uafs_Run`. For every step, workers run their assigned actions sequentially, collect failures as arrays, synchronize at barriers, gather all results to rank 0, and rank 0 emits one pass/fail per step with diagnostics. Workers shut down `AFS::ukernel` before `MPI_Finalize`.

State and persistence: Worker logs are appended to configured files. AFS cache directories and test filesystem paths are mutated by actions. MPI process memory stores step/action state.

Dependencies and integration: Depends on config parsing, action classes, MPI gather/barrier semantics, Test::More, and the SWIG-generated libuafs Perl binding.

Risks: Director has no AFS client and never runs actions. Any worker `die` can abort MPI execution. Results are gathered only after a barrier, so hung actions hang the step. Log files are append-only and can grow.

Test signals: MPI size less than two, rank mapping, one failing worker action, multiple failures, named and unnamed steps, log redirection, uafs setup errors, and shutdown/finalize behavior.
