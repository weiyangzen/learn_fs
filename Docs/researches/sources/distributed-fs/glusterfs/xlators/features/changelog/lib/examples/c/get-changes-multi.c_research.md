# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/c/get-changes-multi.c

Purpose: this C example demonstrates the generic multi-brick changelog callback API. It registers two bricks, filters for bitrot release events, and prints callback notifications.

Important functions: `brick_init`, `brick_fini`, and `brick_callback` satisfy the `gf_brick_spec` lifecycle/callback contract. `fill_brick_spec` populates brick path, event filter, and callback pointers. `main` allocates two specs, initializes changelog, and calls `gf_changelog_register_generic`.

Control flow: after registration, the example calls `select(0, NULL, NULL, NULL, NULL)` to sleep forever while the changelog library's callback machinery invokes `brick_callback`. It uses unordered events by passing `0` for the order flag.

State and persistence behavior: no changelog files are explicitly scanned or marked done by this example. State lives in the library connection and event callback machinery.

Dependencies and integration points: depends on `changelog.h` and `libgfchangelog`. It mirrors the same generic API style used by bitrot daemon, though bitrot passes one brick at a time and sets ordered events.

Risks: the example leaks `strdup` paths and the allocated brick array on failure, which is acceptable for a sample but not a service pattern. It hardcodes example brick paths and logs to `/tmp/multi-changes.log`.

Test signals: compile with pkg-config flags, register two test bricks, inject `CHANGELOG_OP_TYPE_BR_RELEASE`, and verify callbacks include the brick path and event type.
