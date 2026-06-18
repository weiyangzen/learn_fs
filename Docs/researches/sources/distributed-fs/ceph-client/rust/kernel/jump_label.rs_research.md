# sources/distributed-fs/ceph-client/rust/kernel/jump_label.rs

Purpose: exposes Rust support for Linux static keys / jump labels. It lets Rust code branch on a C-defined static key using the architecture-generated static branch assembly when jump labels are enabled, or `static_key_count` otherwise.

Important APIs/types/functions: `static_branch_unlikely!`, hidden `arch_static_branch!`, and `bool_to_int`. `static_branch_unlikely!` accepts the key path, key type, and field name containing the `static_key_false`.

Control flow: the public macro takes an address of the static C key field, casts it to `static_key`, and either calls `bindings::static_key_count` when `CONFIG_JUMP_LABEL` is off or emits an inline assembly block from `generated_arch_static_branch_asm.rs` when enabled. The assembly label path breaks out of a Rust labeled block with `true`; fallthrough returns `false`.

State and persistence behavior: this file owns no state. It observes static key state managed by the C kernel. Generated assembly is included from `OBJTREE`, so build output must contain the expected generated Rust assembly fragment.

Dependencies and integration points: depends on `bindings::static_key_false`, `bindings::static_key`, `static_key_count`, the crate-level `asm!` wrapper, `offset_of!`, and generated architecture files. It is used by Rust features that need low-overhead rarely-enabled branches.

Risks: misuse with a non-static or wrong field type can produce invalid pointer casts or wrong assembly relocation data; the macro is documented as safety-sensitive. Generated assembly inclusion ties correctness to build-system generation. The fallback path mutably casts the static key for `static_key_count`, so the C API assumptions must remain valid.

Test signals: build coverage with and without `CONFIG_JUMP_LABEL` is important. Static-key behavior should be validated by callers toggling keys from C and observing Rust branch behavior. The const include assertion is a build-time signal that the generated assembly fragment evaluates to a string literal.
