<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/random.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/random.c

Purpose: registers a UML hardware RNG provider backed by the host `/dev/random`.

Important APIs/types/functions: global state is `random_fd`, `hwrng`, and completion `have_data`. Key functions are `rng_dev_read()`, `random_interrupt()`, `rng_init()`, `cleanup()`, and `rng_cleanup()`.

Control flow: init opens host `/dev/random`, registers a UML read IRQ on the FD, marks SIGIO broken, fills `hwrng.name/read`, and registers with the hwrng core. Reads call `os_read_file()`; blocking reads temporarily add the FD to SIGIO monitoring, wait for completion, remove monitoring, and deactivate the FD IRQ before retry/return. The IRQ handler completes the wait.

State and persistence: runtime state is the host random FD and hwrng registration. No entropy is persisted by this driver.

Dependencies and integration points: depends on hwrng core, UML IRQ/SIGIO helpers, host `/dev/random`, completions, and module/exitcall cleanup.

Risks: cleanup differs between module exit and UML exitcall; double-close/free paths should be checked. Blocking waits must handle signals and avoid leaving SIGIO registrations active. Reading host `/dev/random` can block depending on host entropy policy.

Test signals: boot with UML_RANDOM, inspect hwrng registration, read from guest hwrng paths, block/unblock behavior under low entropy, unload module, and UML shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/random.c -->
