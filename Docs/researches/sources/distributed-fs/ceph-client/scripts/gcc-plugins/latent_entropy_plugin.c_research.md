# sources/distributed-fs/ceph-client/scripts/gcc-plugins/latent_entropy_plugin.c

Purpose: GCC plugin that implements `__attribute__((latent_entropy))` for kernel functions and variables, adding pseudo-random initialization and instrumentation to feed the kernel's global `latent_entropy`.

Important APIs/functions: Attribute handler validates functions/static variables and initializes integer, integer array, or integer-field struct variables with random constants. `get_random_const()` uses deterministic `-frandom-seed` when present, else `/dev/urandom`. The GIMPLE pass uses `latent_entropy_gate()`, `latent_entropy_execute()`, `init_local_entropy()`, `perturb_local_entropy()`, and `perturb_latent_entropy()`. `latent_entropy_start_unit()` declares external volatile `unsigned long latent_entropy`. `plugin_init()` registers attributes, GGC roots, start-unit callback, and pass info.

Control flow: For marked variables, random initializers are assigned during attribute handling. For marked functions, the pass skips noreturn-like functions, creates a local entropy variable, initializes it with frame address and global entropy, perturbs it in each basic block with rotating add/xor/rotate operations, and writes it back to the global entropy before returns or tail calls.

State/persistence: Maintains GCC GC root `latent_entropy_decl`, deterministic seed, random buffer, index, and `/dev/urandom` fd in the compiler process. It mutates GCC GIMPLE and variable initializers.

Dependencies/integration: Requires GCC plugin internals, `gcc-common.h`, generated GIMPLE pass header, kernel symbol `latent_entropy`, and plugin args such as `disable`.

Risks: Random initializer output is build-environment dependent unless a deterministic seed is supplied. `/dev/urandom` failure asserts. Instrumentation depends on CFG shape, tail-call handling, and SSA updates. Attribute misuse produces compile errors. Not cryptographic entropy, as documented.

Test signals: Compile marked variables of allowed/disallowed types, marked functions with branches and tail calls, noreturn functions, deterministic seed builds for reproducibility, disabled plugin, and runtime presence of global `latent_entropy`.
