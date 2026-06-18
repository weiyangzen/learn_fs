## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/error.h

### Purpose
`compressed/error.h` declares compressed boot warning and fatal-error APIs with noreturn/cold annotations.

### Important APIs, Types, And Functions
It declares `warn(const char *m)`, `error(char *m) __noreturn`, and `panic(const char *fmt, ...) __noreturn __cold`.

### Control Flow
The header has no control flow; it supplies function contracts for callers and compiler analysis.

### State, Persistence, And Dependencies
No state is defined. It depends on `linux/compiler.h` for annotations.

### Integration Points
Included by compressed boot C files that need fatal diagnostics without depending directly on `misc.c` internals.

### Risks
The `error()` prototype takes `char *` rather than `const char *`, matching existing implementation but potentially requiring casts for literal-correct code. Noreturn annotations must match behavior.

### Test Signals
Compile all compressed boot objects with warnings enabled and check that noreturn paths suppress false fallthrough diagnostics.
