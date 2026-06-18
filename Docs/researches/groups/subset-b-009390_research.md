# subset-b-009390 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ustat.c -->
# sources/test-tools/stress-ng/test/test-ustat.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `the obsolete `ustat(2)` interface`. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `sys/types.h`, `unistd.h`, `ustat.h`, and Linux `sys/sysmacros.h` for `makedev()`, declares the relevant object or arguments, and then builds a block-device `dev_t`, declares `struct ustat`, and calls `ustat(dev, &ubuf)`. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the file deliberately errors out on GNU Hurd and aarch64 because the interface is absent or always fails there. On modern libc/kernel combinations `ustat` may be deprecated, hidden, or link-compatible but unusable at runtime.

Test signals: compile success proves the header, `struct ustat`, `makedev`, and symbol are visible; compile failure or the explicit `#error` disables dependent stress-ng code. Runtime failure is expected on many systems and should not be read as persistent state damage.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ustat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-utimbuf.c -->
# sources/test-tools/stress-ng/test/test-utimbuf.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``struct utimbuf` availability`. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `utime.h` and `string.h`, declares the relevant object or arguments, and then zeroes a `struct utimbuf` and returns `sizeof(buf)`. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the return value is not semantically meaningful as a process status beyond being nonzero; this probe is mainly for compile/link detection. Some strict build modes can warn on returning `sizeof` through `int`, but the object is small.

Test signals: presence of `utime.h` and `struct utimbuf` is the main signal; no filesystem timestamp is changed.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-utimbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-utime.c -->
# sources/test-tools/stress-ng/test/test-utime.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``utime(2)` and `struct utimbuf``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `utime.h` and `string.h`, declares the relevant object or arguments, and then zeroes a `struct utimbuf` and calls `utime(".", &buf)`. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: if executed, it attempts to set the current directory timestamps to the epoch and may fail on permission or filesystem policy. Configure runs should account for side effects or run in disposable working directories.

Test signals: compile/link success proves `utime` is callable; runtime success or expected permission failures verify the wrapper exists.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-utime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-utimensat.c -->
# sources/test-tools/stress-ng/test/test-utimensat.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``utimensat(2)``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `string.h`, `fcntl.h`, and `sys/stat.h` with `_GNU_SOURCE`, declares the relevant object or arguments, and then zeroes a two-element `timespec` array and calls `utimensat(0, "/tmp", times, 0)`. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: runtime execution may try to change `/tmp` timestamps and normally requires ownership/permissions. The first argument is `0` rather than `AT_FDCWD`, but the absolute path makes the descriptor irrelevant.

Test signals: compile success proves the prototype and `struct timespec` are available; runtime status shows whether the libc/kernel pair accepts the call.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-utimensat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-utimes.c -->
# sources/test-tools/stress-ng/test/test-utimes.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``utimes(2)``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `utime.h` and `sys/time.h`, declares the relevant object or arguments, and then initializes two `struct timeval` entries to zero and calls `utimes(".", times)`. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: if executed, this can alter current-directory timestamps or fail under permissions, immutable filesystems, or sandboxing.

Test signals: the configure signal is successful compilation and symbol resolution for `utimes`; runtime return distinguishes availability from permission failure.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-utimes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v2di.c -->
# sources/test-tools/stress-ng/test/test-v2di.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `the GCC/Clang vector type `__v2di` from x86 SIMD headers`. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `xmmintrin.h`, declares the relevant object or arguments, and then declares a constant `__v2di` vector and returns its size. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the probe is architecture/compiler specific; non-x86 targets or compilers without this typedef fail at compile time. It does not execute SIMD instructions directly.

Test signals: compile success is the relevant signal for enabling vectorized stress-ng code that names `__v2di`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v2di.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_audio.c -->
# sources/test-tools/stress-ng/test/test-v4l2_audio.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `Linux V4L2 type `struct v4l2_audio``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `linux/videodev2.h`, declares the relevant object or arguments, and then declares `struct v4l2_audio`, marks it used, and returns its size. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the API is Linux UAPI-header dependent; older or non-Linux systems may lack the type even if other V4L2 definitions exist. Runtime has no device interaction, so it cannot validate ioctl behavior.

Test signals: compile success confirms the header exposes `struct v4l2_audio` for stress-ng V4L2 stressors; failure should disable only code paths requiring that exact type.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_audioout.c -->
# sources/test-tools/stress-ng/test/test-v4l2_audioout.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `Linux V4L2 type `struct v4l2_audioout``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `linux/videodev2.h`, declares the relevant object or arguments, and then declares `struct v4l2_audioout`, marks it used, and returns its size. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the API is Linux UAPI-header dependent; older or non-Linux systems may lack the type even if other V4L2 definitions exist. Runtime has no device interaction, so it cannot validate ioctl behavior.

Test signals: compile success confirms the header exposes `struct v4l2_audioout` for stress-ng V4L2 stressors; failure should disable only code paths requiring that exact type.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_audioout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_capability.c -->
# sources/test-tools/stress-ng/test/test-v4l2_capability.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `Linux V4L2 type `struct v4l2_capability``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `linux/videodev2.h`, declares the relevant object or arguments, and then declares `struct v4l2_capability`, marks it used, and returns its size. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the API is Linux UAPI-header dependent; older or non-Linux systems may lack the type even if other V4L2 definitions exist. Runtime has no device interaction, so it cannot validate ioctl behavior.

Test signals: compile success confirms the header exposes `struct v4l2_capability` for stress-ng V4L2 stressors; failure should disable only code paths requiring that exact type.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_capability.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_dv_timings.c -->
# sources/test-tools/stress-ng/test/test-v4l2_dv_timings.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `Linux V4L2 type `struct v4l2_dv_timings``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `linux/videodev2.h`, declares the relevant object or arguments, and then declares `struct v4l2_dv_timings`, marks it used, and returns its size. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the API is Linux UAPI-header dependent; older or non-Linux systems may lack the type even if other V4L2 definitions exist. Runtime has no device interaction, so it cannot validate ioctl behavior.

Test signals: compile success confirms the header exposes `struct v4l2_dv_timings` for stress-ng V4L2 stressors; failure should disable only code paths requiring that exact type.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_dv_timings.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_enc_idx.c -->
# sources/test-tools/stress-ng/test/test-v4l2_enc_idx.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `Linux V4L2 type `struct v4l2_enc_idx``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `linux/videodev2.h`, declares the relevant object or arguments, and then declares `struct v4l2_enc_idx`, marks it used, and returns its size. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the API is Linux UAPI-header dependent; older or non-Linux systems may lack the type even if other V4L2 definitions exist. Runtime has no device interaction, so it cannot validate ioctl behavior.

Test signals: compile success confirms the header exposes `struct v4l2_enc_idx` for stress-ng V4L2 stressors; failure should disable only code paths requiring that exact type.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_enc_idx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_framebuffer.c -->
# sources/test-tools/stress-ng/test/test-v4l2_framebuffer.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `Linux V4L2 type `struct v4l2_framebuffer``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `linux/videodev2.h`, declares the relevant object or arguments, and then declares `struct v4l2_framebuffer`, marks it used, and returns its size. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the API is Linux UAPI-header dependent; older or non-Linux systems may lack the type even if other V4L2 definitions exist. Runtime has no device interaction, so it cannot validate ioctl behavior.

Test signals: compile success confirms the header exposes `struct v4l2_framebuffer` for stress-ng V4L2 stressors; failure should disable only code paths requiring that exact type.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_framebuffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_jpegcompression.c -->
# sources/test-tools/stress-ng/test/test-v4l2_jpegcompression.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `Linux V4L2 type `struct v4l2_jpegcompression``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `linux/videodev2.h`, declares the relevant object or arguments, and then declares `struct v4l2_jpegcompression`, marks it used, and returns its size. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the API is Linux UAPI-header dependent; older or non-Linux systems may lack the type even if other V4L2 definitions exist. Runtime has no device interaction, so it cannot validate ioctl behavior.

Test signals: compile success confirms the header exposes `struct v4l2_jpegcompression` for stress-ng V4L2 stressors; failure should disable only code paths requiring that exact type.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_jpegcompression.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_std_id.c -->
# sources/test-tools/stress-ng/test/test-v4l2_std_id.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `Linux V4L2 type `v4l2_std_id``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `linux/videodev2.h`, declares the relevant object or arguments, and then declares `v4l2_std_id`, marks it used, and returns its size. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the API is Linux UAPI-header dependent; older or non-Linux systems may lack the type even if other V4L2 definitions exist. Runtime has no device interaction, so it cannot validate ioctl behavior.

Test signals: compile success confirms the header exposes `v4l2_std_id` for stress-ng V4L2 stressors; failure should disable only code paths requiring that exact type.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-v4l2_std_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-valloc.c -->
# sources/test-tools/stress-ng/test/test-valloc.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``valloc(3)``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `stdlib.h` and `malloc.h`, declares the relevant object or arguments, and then allocates 1024 bytes with `valloc`, frees it if non-null, and returns zero. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: `valloc` is obsolete and may be hidden by feature-test macros or absent on non-glibc platforms. Allocation failure is ignored because the probe targets symbol availability rather than memory health.

Test signals: compile/link success and a clean run indicate the symbol is usable enough for stress-ng compatibility code.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-valloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vfork.c -->
# sources/test-tools/stress-ng/test/test-vfork.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``vfork(2)``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `unistd.h` and `stdlib.h`, declares the relevant object or arguments, and then calls `vfork()` and immediately exits through `_exit((int)pid)`. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: `vfork` has strict parent/child semantics: the child must not return or mutate parent state before `_exit`/`exec`. This probe follows that rule, but its process exit code varies depending on parent versus child path.

Test signals: compile success confirms the prototype; runtime should terminate promptly without running normal `exit` handlers.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vfork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vhangup.c -->
# sources/test-tools/stress-ng/test/test-vhangup.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``vhangup(2)``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `unistd.h`, declares the relevant object or arguments, and then returns the result of `vhangup()`. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: `vhangup` is privileged on many systems and can affect controlling terminals if actually permitted. Configure execution should expect `EPERM` in unprivileged environments.

Test signals: compile/link success is enough to expose the wrapper; runtime permission failure is a normal signal, not a stress-ng bug.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vhangup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vla-arg.c -->
# sources/test-tools/stress-ng/test/test-vla-arg.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `C variable-length array function parameters`. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes no external headers, declares the relevant object or arguments, and then defines `vla_arg_func(int n, int array[n])`, passes a fixed local array, and returns zero. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the probe depends on compiler language mode. C11 optional VLA support, C++ compilation, or strict flags disabling VLAs will fail even though the runtime logic is trivial.

Test signals: compile success tells stress-ng that VLA parameter syntax can be used; no OS or libc state is involved.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vla-arg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vmsplice.c -->
# sources/test-tools/stress-ng/test/test-vmsplice.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``vmsplice(2)``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `fcntl.h` and `sys/uio.h` with `_GNU_SOURCE`, declares the relevant object or arguments, and then creates an empty `iovec` and calls `vmsplice(3, &iov, 1, 0)`. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the file intentionally uses a dummy fd, so execution will normally fail with `EBADF`; the aim is prototype/link detection. The syscall is Linux-specific and may be blocked by seccomp.

Test signals: compile/link success confirms libc exposes `vmsplice`; runtime failure with a normal errno still validates callability.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vmsplice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vt_consize.c -->
# sources/test-tools/stress-ng/test/test-vt_consize.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `Linux virtual-terminal type `struct vt_consize``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `linux/vt.h`, declares the relevant object or arguments, and then declares `struct vt_consize`, marks it used, and returns its size. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the probe depends on Linux console UAPI headers. It does not open a tty or issue ioctls, so it cannot validate runtime VT permissions or actual console availability.

Test signals: compile success confirms `struct vt_consize` exists for VT ioctl stressor code; missing headers/types should gate that code out.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vt_consize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vt_mode.c -->
# sources/test-tools/stress-ng/test/test-vt_mode.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `Linux virtual-terminal type `struct vt_mode``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `linux/vt.h`, declares the relevant object or arguments, and then declares `struct vt_mode`, marks it used, and returns its size. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the probe depends on Linux console UAPI headers. It does not open a tty or issue ioctls, so it cannot validate runtime VT permissions or actual console availability.

Test signals: compile success confirms `struct vt_mode` exists for VT ioctl stressor code; missing headers/types should gate that code out.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vt_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vt_sizes.c -->
# sources/test-tools/stress-ng/test/test-vt_sizes.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `Linux virtual-terminal type `struct vt_sizes``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `linux/vt.h`, declares the relevant object or arguments, and then declares `struct vt_sizes`, marks it used, and returns its size. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the probe depends on Linux console UAPI headers. It does not open a tty or issue ioctls, so it cannot validate runtime VT permissions or actual console availability.

Test signals: compile success confirms `struct vt_sizes` exists for VT ioctl stressor code; missing headers/types should gate that code out.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vt_sizes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vt_stat.c -->
# sources/test-tools/stress-ng/test/test-vt_stat.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `Linux virtual-terminal type `struct vt_stat``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `linux/vt.h`, declares the relevant object or arguments, and then declares `struct vt_stat`, marks it used, and returns its size. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the probe depends on Linux console UAPI headers. It does not open a tty or issue ioctls, so it cannot validate runtime VT permissions or actual console availability.

Test signals: compile success confirms `struct vt_stat` exists for VT ioctl stressor code; missing headers/types should gate that code out.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-vt_stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-wait3.c -->
# sources/test-tools/stress-ng/test/test-wait3.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``wait3(2)``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `sys/types.h`, `sys/time.h`, `sys/resource.h`, `sys/wait.h`, and `unistd.h` with `_GNU_SOURCE`, declares the relevant object or arguments, and then declares `status` and `struct rusage`, then calls `wait3(&status, 0, &rusage)`. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: with no child process this likely returns `ECHILD`; that is expected. Some libc implementations omit BSD wait interfaces unless feature macros are set.

Test signals: compile/link success proves `wait3` and `struct rusage` are available; runtime return verifies the wrapper path.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-wait3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-wait4.c -->
# sources/test-tools/stress-ng/test/test-wait4.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``wait4(2)``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `sys/types.h`, `sys/time.h`, `sys/resource.h`, `sys/wait.h`, and `unistd.h` with `_GNU_SOURCE`, declares the relevant object or arguments, and then calls `wait4(getpid(), &status, 0, &rusage)`. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: waiting on the current process is not a successful reap scenario and should fail at runtime. The probe is for symbol/prototype detection and rusage typing.

Test signals: compile/link success enables wait4-dependent stress-ng logic; runtime failure with normal wait errno is acceptable.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-wait4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-waitid.c -->
# sources/test-tools/stress-ng/test/test-waitid.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``waitid(2)``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `sys/types.h`, `sys/wait.h`, and `unistd.h` with `_GNU_SOURCE`, declares the relevant object or arguments, and then declares `siginfo_t` and calls `waitid(P_PID, getpid(), &info, 0)`. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the options argument is zero, so runtime may fail with `EINVAL` or `ECHILD` depending on implementation; this is not a behavioral wait test.

Test signals: compile success confirms `siginfo_t`, `P_PID`, and `waitid` are visible.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-waitid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-waitpid.c -->
# sources/test-tools/stress-ng/test/test-waitpid.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``waitpid(2)``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `sys/wait.h` with `_GNU_SOURCE`, declares the relevant object or arguments, and then calls `waitpid(999999, &status, 0)` and casts the result to `int`. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the hard-coded PID is expected not to be a child and runtime should fail. The cast is safe for configure purposes but not a general wait abstraction.

Test signals: compile/link success is the main signal; runtime should not block because the PID is not a child of the process.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-waitpid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-wchar.c -->
# sources/test-tools/stress-ng/test/test-wchar.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``wchar.h` availability`. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `wchar.h`, declares the relevant object or arguments, and then does nothing except return zero from `main()`. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: this is purely a header presence probe and does not verify individual wide-character functions or locale behavior.

Test signals: compile success confirms the header can be included by stress-ng code.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-wchar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-wcsfunc.c -->
# sources/test-tools/stress-ng/test/test-wcsfunc.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around `platform-specific wide-character function availability via `WCSFUNC``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes BSD or libbsd headers plus `wchar.h`, selected by OS macros, declares the relevant object or arguments, and then places the macro-expanded `WCSFUNC` symbol into a static function-pointer array and checks whether the first pointer is null. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: `WCSFUNC` must be supplied by the configure harness, so standalone compilation without that definition fails. Header paths differ across BSD, GNU/libbsd, and GNU/kFreeBSD, making this a portability-sensitive probe.

Test signals: successful compilation proves the requested wide-character function is declared in the selected header set; link/runtime confirms the symbol can be referenced.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-wcsfunc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-winsize.c -->
# sources/test-tools/stress-ng/test/test-winsize.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``struct winsize``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `sys/ioctl.h`, declares the relevant object or arguments, and then declares `struct winsize`, marks it used, and returns its size. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: the probe only checks type visibility, not terminal ioctl behavior. Non-POSIX or reduced libc environments may omit the definition.

Test signals: compile success enables code that stores or exchanges terminal window size values.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-winsize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-writev.c -->
# sources/test-tools/stress-ng/test/test-writev.c research

Purpose: compile-time and smoke-runtime probe for stress-ng feature detection around ``writev(2)``. It lets the stress-ng build configure whether the platform exposes the requested header, type, syscall wrapper, or libc symbol before enabling code paths that depend on it.

Important APIs, types, and functions: the only function is `main()`. It includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/uio.h`, and `unistd.h` with `_GNU_SOURCE`, declares the relevant object or arguments, and then opens `/dev/null`, writes one `iovec` buffer with `writev`, closes the fd, and returns the byte count or open failure. There is no project-local type or helper API in this file; its public signal is successful compilation and, when the configure harness executes it, the process exit status.

Control flow: execution is linear: initialize any required local storage, call or size-check the probed API, and return the result. There are no loops, callbacks, or branches except simple cleanup/error paths where applicable.

State and persistence: state is limited to stack locals and any transient kernel/libc side effect from the probed call. No repository state is persisted. Runtime calls that touch the current directory, `/tmp`, `/dev/null`, or process wait state are intended as configure probes rather than application behavior.

Dependencies and integration: this file integrates with the stress-ng test/configure suite under `sources/test-tools/stress-ng/test`. A successful compile typically controls `HAVE_*` feature macros used by stress-ng stressors and shim code.

Risks: runtime depends on `/dev/null` existing and being writable. The return value is a positive byte count on success, which configure harnesses must interpret correctly if they expect zero-only success.

Test signals: compile/link success confirms `struct iovec` and `writev`; runtime success confirms a simple vector write path.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-writev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/ISSUE_TEMPLATE/config.yml -->
# sources/test-tools/syzkaller/.github/ISSUE_TEMPLATE/config.yml research

Purpose: GitHub issue-template configuration for the syzkaller repository. It disables blank issues and redirects general questions to the public syzkaller mailing list.

Important APIs, types, and functions: this is declarative GitHub metadata using `blank_issues_enabled` and `contact_links`. The single contact link has `name`, `url`, and `about` fields.

Control flow: GitHub reads this file when rendering the new-issue UI. There is no local execution path.

State and persistence: it persists repository policy in source control only. The runtime state is GitHub's issue creation UI behavior.

Dependencies and integration: integrated by GitHub under `.github/ISSUE_TEMPLATE/config.yml`; the mailing-list URL is the external support integration point.

Risks: disabling blank issues may push valid bug reports away if no suitable issue form exists. The support link must remain current.

Test signals: opening the repository's new issue page should show blank issues disabled and the mailing-list contact option.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/ISSUE_TEMPLATE/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/arc_config/values.yaml -->
# sources/test-tools/syzkaller/.github/arc_config/values.yaml research

Purpose: Helm values for deploying GitHub Actions Runner Controller scale-set runners for the syzkaller repository.

Important APIs, types, and functions: key fields include `githubConfigUrl`, `githubConfigSecret`, `containerMode.type: kubernetes`, a Kubernetes-mode PVC template with `ReadWriteOnce`, `openebs-hostpath`, and 1 Gi storage, plus a runner pod template requesting 31 CPUs.

Control flow: ARC and its Helm chart consume this values file to create listener and runner pods. Jobs execute inside Kubernetes-mode runner pods rather than Docker-in-Docker.

State and persistence: persistent state is external to the file: Kubernetes secrets, PVCs, runner registrations, and ephemeral work volumes. The checked-in file leaves `github_token` empty, so live credentials must be supplied separately.

Dependencies and integration: depends on the ARC chart, a compatible Kubernetes cluster, a storage class named `openebs-hostpath`, GitHub runner registration permissions, and high-CPU nodes.

Risks: an empty secret is safe for source control but unusable without deployment-time secret injection. The 31-CPU request can starve scheduling on smaller clusters. Kubernetes container mode requires job containers and volume behavior compatible with the workflows.

Test signals: Helm template/lint output, kube-linter findings, successful listener startup, runner registration in GitHub, PVC provisioning, and a CI job landing on a scale-set runner.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/arc_config/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/codecov.yml -->
# sources/test-tools/syzkaller/.github/codecov.yml research

Purpose: Codecov configuration for syzkaller coverage uploads.

Important APIs, types, and functions: it disables `require_ci_to_pass`, sets coverage display precision/range, makes project and patch statuses informational with threshold 100 percent and target 0 percent, configures comments after two builds, disables GitHub check annotations, and rewrites checkout paths with `fixes`.

Control flow: Codecov reads this file during upload, normalizes paths from the GitHub Actions GOPATH checkout, and posts informational coverage results and file-oriented comments.

State and persistence: the file stores reporting policy only. Coverage data is uploaded by CI artifacts and Codecov's service.

Dependencies and integration: used by `.github/workflows/upload-coverage.yml`, which points the Codecov action at the trusted base-repository copy.

Risks: informational statuses avoid blocking PRs even on large coverage regressions. The broad 100 percent threshold and 0 percent target make the status intentionally non-gating. Path fixes must match the CI checkout path.

Test signals: Codecov validation, successful unittests/dashboard flag uploads, correctly normalized file paths, and a comment appearing after both expected coverage artifacts are processed.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/codecov.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/dependabot.yml -->
# sources/test-tools/syzkaller/.github/dependabot.yml research

Purpose: Dependabot version-update configuration for Go modules in syzkaller.

Important APIs, types, and functions: declares version 2 config with one `gomod` update block rooted at `/`, monthly schedule, five open PR limit, commit prefix `mod:`, and assignee `tarasmadan`.

Control flow: GitHub Dependabot periodically scans `go.mod`/`go.sum`, opens dependency-update PRs up to the configured limit, and applies the commit-message convention.

State and persistence: no runtime state in the repository beyond this policy; Dependabot tracks scheduled checks and PRs in GitHub.

Dependencies and integration: integrated by GitHub code security/dependency tooling and the Go module graph.

Risks: monthly cadence can leave vulnerable or breaking dependency changes queued for weeks. A single assignee is an ownership bottleneck if inactive.

Test signals: Dependabot insights should show an active gomod ecosystem, generated PR titles/commits should use `mod:`, and no more than five open update PRs should be active.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/ci.yml -->
# sources/test-tools/syzkaller/.github/workflows/ci.yml research

Purpose: main GitHub Actions CI workflow for syzkaller pushes and pull requests.

Important APIs, types, and functions: jobs include `aux`, `build`, `dashboard`, architecture matrix, race tests, old environment, and gVisor smoke testing. It uses pinned checkout/cache/upload-artifact actions, container images such as `gcr.io/syzkaller/env:latest`, `old-env`, and `syzbot`, GOPATH-style checkout paths, and `.github/workflows/run.sh` to format errors.

Control flow: pushes and PRs start a concurrency group that cancels older runs for the same PR/ref. `aux` runs `make presubmit_aux`; `build` runs `make presubmit_build` and uploads unit coverage; `dashboard` runs `make presubmit_dashboard` with a timeout and uploads dashboard coverage; `arch` fans out make targets for OS/arch builds; race jobs run race presubmits; `old` verifies older build environment support; `gvisor` builds then runs the gVisor smoke script in a privileged container.

State and persistence: CI state is limited to GitHub caches under `/syzkaller/.cache`, coverage artifacts, and job logs. The repository checkout is under `gopath/src/github.com/google/syzkaller` to satisfy tooling assumptions.

Dependencies and integration: integrates with the syzkaller Makefile presubmit targets, Google container images, GitHub cache/artifact services, and the privileged gVisor smoke environment.

Risks: container tags are mutable even when actions are SHA-pinned. `oss-fuzz` and gVisor coverage are separate, so this file's green status is not total ecosystem validation. Timeouts and high-core runner labels can cause infrastructure-dependent flakes.

Test signals: job matrix completion, uploaded `.coverage.txt` artifacts named `coverage-unittests` and `coverage-dashboard`, cache restore/update behavior, formatted annotations from `run.sh`, and cancellation of superseded PR runs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/depsreview.yaml -->
# sources/test-tools/syzkaller/.github/workflows/depsreview.yaml research

Purpose: pull-request dependency review workflow.

Important APIs, types, and functions: grants read-only contents permission, checks out the repository with a SHA-pinned `actions/checkout`, then runs a SHA-pinned `actions/dependency-review-action`.

Control flow: every pull request triggers a single `dependency-review` job on `ubuntu-latest`. The action compares dependency changes and reports policy/security findings.

State and persistence: no repository state is modified. Results are stored as GitHub checks/logs.

Dependencies and integration: depends on GitHub's dependency graph and the dependency-review action.

Risks: the action and checkout are pinned, but the runner image is not. Findings depend on supported ecosystems and GitHub advisory data.

Test signals: PR checks should include Dependency Review, fail or warn according to dependency-review defaults, and show only read permissions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/depsreview.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/oss-fuzz.yml -->
# sources/test-tools/syzkaller/.github/workflows/oss-fuzz.yml research

Purpose: CI fuzzing workflow that builds and runs syzkaller fuzzers through OSS-Fuzz CIFuzz on pull requests.

Important APIs, types, and functions: uses `google/oss-fuzz/infra/cifuzz/actions/build_fuzzers@master`, `run_fuzzers@master`, artifact upload on failure, and CodeQL SARIF upload.

Control flow: PRs run the build-fuzzers step, then run fuzzers for 300 seconds with Go language settings and SARIF output. If build succeeded and fuzzing fails, artifacts under `./out/artifacts` are uploaded. SARIF upload runs whenever the build step succeeded.

State and persistence: fuzz build outputs, crash artifacts, and SARIF results are job-local until uploaded as GitHub artifacts/security results.

Dependencies and integration: integrates with OSS-Fuzz project `syzkaller`, GitHub artifact storage, and CodeQL SARIF ingestion.

Risks: actions are referenced by mutable tags (`master`, `v4`, `v2`) rather than full SHAs, unlike the main CI workflow. A 300-second fuzz window is good for regression smoke testing but not deep fuzzing.

Test signals: successful fuzzer build, five-minute CIFuzz execution, uploaded crash artifacts on failure, and SARIF results visible in GitHub code scanning.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/oss-fuzz.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/run.sh -->
# sources/test-tools/syzkaller/.github/workflows/run.sh research

Purpose: wrapper script for GitHub Actions CI commands that sets a stable home/cache directory and converts compiler/test diagnostics into GitHub workflow annotations.

Important APIs, types, and functions: Bash script with `HOME=$PWD`, `.cache` creation, `set -o pipefail`, positional command execution `$1 "${@:2}"`, and a `sed -E` regex that emits `::error file=...,line=...,col=...::...` records.

Control flow: the script runs the requested command, pipes combined stdout through `sed`, and relies on `pipefail` so command failures propagate through the annotation pipeline.

State and persistence: creates `.cache` under the checkout and exports `HOME` for tools that consult user cache/config directories. It does not mutate source files directly.

Dependencies and integration: invoked by `ci.yml` for Makefile presubmit targets. Depends on Bash and GNU/BSD-compatible `sed -E`.

Risks: annotation regex can misclassify arbitrary output that resembles `file:line:` diagnostics. Commands that require stdin interaction are not supported. The script does not quote the command name beyond positional expansion, so callers must pass arguments normally.

Test signals: failing compiler/linter output should appear both as raw log lines and GitHub error annotations; the wrapper should return nonzero when the underlying command fails.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/upload-coverage.yml -->
# sources/test-tools/syzkaller/.github/workflows/upload-coverage.yml research

Purpose: privileged coverage upload workflow that runs after successful `ci` workflow runs and publishes unit/dashboard coverage to Codecov.

Important APIs, types, and functions: triggered by `workflow_run` completion for workflow `ci`, with read-only contents/actions permissions. It uses SHA-pinned checkout, download-artifact, and Codecov actions, checks out untrusted head code without persisted credentials, checks out the trusted base `.github/codecov.yml`, fetches a PR number with `gh pr list`, and uploads two named coverage artifacts with separate Codecov flags.

Control flow: the job runs only when the upstream CI conclusion is `success`. It checks out the head repository/commit, checks out a sparse trusted base config into `base-repo`, downloads artifacts for the triggering run id, resolves PR number from the head SHA or workflow payload, then uploads `coverage-unittests` and `coverage-dashboard` with override commit/PR values.

State and persistence: consumes GitHub artifacts and secrets (`CODECOV_TOKEN`, `GITHUB_TOKEN`) in a privileged base-repository context. It persists coverage only to Codecov.

Dependencies and integration: integrates with artifact names emitted by `ci.yml`, Codecov configuration, GitHub CLI, repository secrets, and the `workflow_run` trust boundary.

Risks: the comments document the key security issue: this privileged workflow checks out untrusted fork code. `persist-credentials: false`, trusted sparse config checkout, pinned actions, and explicit artifact run id reduce that risk, but any future step that executes untrusted code here would be dangerous.

Test signals: workflow should skip failed CI runs, download the expected two artifacts, resolve PR numbers for fork PRs, and show Codecov uploads against the head SHA rather than the default branch workflow commit.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/upload-coverage.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.golangci.yml -->
# sources/test-tools/syzkaller/.golangci.yml research

Purpose: golangci-lint configuration for syzkaller's Go code.

Important APIs, types, and functions: config version 2, eight-minute timeout, `codeanalysis` build tag, text output without issued lines, `gofmt` formatter, a custom `syz-linter` plugin at `bin/syz-linter.so`, and a curated set of enabled linters including `dupl`, `gocognit`, `gocritic`, `govet`, `staticcheck`, `unused`, and `whitespace`.

Control flow: `make lint` builds the plugin and runs `bin/golangci-lint run ./...`, which consumes this file. Exclusions relax selected checks for generated files, tests, `prog`, trace parser code, and known style exceptions.

State and persistence: this file stores lint policy. Runtime state is golangci-lint cache and generated plugin binary.

Dependencies and integration: depends on golangci-lint v2 semantics, the locally built syz-linter plugin, keep-sorted formatting for linter lists, and Makefile lint targets.

Risks: high thresholds for function length, cognitive complexity, and cyclomatic complexity allow large functions to remain. Several useful linters such as `errcheck`, `gosec`, and `unparam` are disabled due existing debt or project tradeoffs.

Test signals: `make lint` should honor the custom plugin, report unused exclusions, keep sorted blocks stable, and avoid findings in generated/test paths covered by exclusions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.kube-linter.yaml -->
# sources/test-tools/syzkaller/.kube-linter.yaml research

Purpose: kube-linter policy file for syzkaller Kubernetes manifests.

Important APIs, types, and functions: enables default checks by leaving `doNotAutoAddDefaults: false` and excludes checks such as latest image tags, read-only root filesystems, non-root execution, CPU/memory requirements, privilege escalation, privileged containers, anti-affinity, and dangling services.

Control flow: `make presubmit_aux` invokes `check_k8s`, which is expected to run kube-linter with this configuration against Kubernetes manifests.

State and persistence: declarative lint policy only; no cluster state is changed.

Dependencies and integration: depends on kube-linter and syzkaller's fuzzer infrastructure manifests, where privileged/root/nested-VM behavior is often intentional.

Risks: the exclusions intentionally suppress several security best-practice checks. That is defensible for fuzzer infrastructure but can hide accidental privilege expansion in less trusted deployment surfaces.

Test signals: kube-linter should still run default checks outside the excluded set, and presubmit should fail on non-excluded manifest regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.kube-linter.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.mockery.yaml -->
# sources/test-tools/syzkaller/.mockery.yaml research

Purpose: mockery configuration for generating Go mocks for selected syzkaller interfaces.

Important APIs, types, and functions: global templates set output directory to `{{.InterfaceDir}}/mocks`, package `mocks`, struct and filename from interface names. Package entries generate mocks for GCS `Client`, covermerger `FileVersProvider`, coveragedb Spanner interfaces, rpcserver `Manager`, proxyrpc `ProxyAppInterface`, and proxyapp `subProcessCmd` with package-specific output overrides.

Control flow: `make generate_go` runs `go tool mockery --log-level="error"`, which reads this file and rewrites generated mocks.

State and persistence: generated mock Go files are persisted in package-specific `mocks` directories. This config is the source of truth for which interfaces are regenerated.

Dependencies and integration: depends on mockery, interface names remaining stable, and Makefile generation targets.

Risks: moving interfaces or renaming unexported `subProcessCmd` requires config updates. Generated output churn can occur across mockery versions if templates/defaults change.

Test signals: `make generate_go` should complete without missing-interface errors and `make check_diff` should stay clean after regeneration.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.mockery.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/Makefile -->
# sources/test-tools/syzkaller/Makefile research

Purpose: top-level syzkaller build, generation, formatting, lint, test, and presubmit orchestration.

Important APIs, types, and functions: key variables include host/target OS and arch triplets, `GOFLAGS` with revision ldflags, `CGO_ENABLED`, `GOBIN`, `TARGETGOOS`, and `TARGETGOARCH`. Targets build host tools (`syz-manager`, `syz-ci`, `syz-agent`, `syz-lore-relay`, `syz-repro`, `syz-db`, etc.), target tools/executor, generated syscall descriptions, Go/RPC/syscall generation, formatting, linting, architecture presubmits, race presubmits, and prerequisite installation.

Control flow: `tools/syz-make/make.go` computes environment settings consumed by Make. `all` builds host and target artifacts. `descriptions` installs/runs `syz-sysgen` and updates `.descriptions`. Presubmit targets compose generation, formatting checks, builds, lint, tests, multi-arch target builds, executor variants, dashboard tests, and race tests.

State and persistence: writes build artifacts under `bin/`, generated syscall files under `sys/gen`, executor generated headers, `.descriptions`, coverage files, and generated mocks/RPC code. `clean` removes core build/generated artifacts.

Dependencies and integration: depends on Go modules, C/C++ compilers, clang-format/tidy, flatc, ragel, goyacc, keep-sorted, golangci-lint, syz-linter plugin, kernel source trees for extraction/config targets, and CI wrappers.

Risks: the Makefile drives many generated artifacts, so partial toolchain differences can cause noisy diffs. `CGO_ENABLED=0` is the default except selected targets, which is important for Android/static compatibility. Architecture targets assume cross compilers and platform support discovered by `syz-make`.

Test signals: `make`, `make presubmit`, `make test`, `make lint`, `make generate`, and `make check_diff` are the primary signals. CI maps directly onto many of these presubmit subtargets.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/api/api.go -->
# sources/test-tools/syzkaller/dashboard/api/api.go research

Purpose: stable JSON data model for syzkaller dashboard export/API consumers.

Important APIs, types, and functions: declares `Version = 1` and DTO structs `BugGroup`, `BugSummary`, `Bug`, `Crash`, and `Commit` with JSON tags. The structs describe bug lists, individual bug metadata, crash reproduction/build links, and commit identity/repository fields.

Control flow: there are no functions in this file. The control contract is serialization compatibility: dashboard handlers populate these structs, and clients validate the `Version` field.

State and persistence: no state is stored here. `time.Time` and pointer time fields encode persisted dashboard timestamps when marshaled.

Dependencies and integration: imported by API clients and dashboard JSON endpoints; `client.go` reflects on the `Version` field after unmarshalling.

Risks: all structures are documented as backwards compatible, so removing/renaming fields or changing JSON tags breaks external consumers. Version remains coarse-grained, so additive changes must remain optional.

Test signals: JSON round trips, API client version checks, and consumers handling omitted optional fields are the main validation points.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/api/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/api/client.go -->
# sources/test-tools/syzkaller/dashboard/api/client.go research

Purpose: Go client helper for reading syzkaller dashboard JSON API endpoints and text artifacts.

Important APIs, types, and functions: `Client` stores base URL, OAuth token, throttling flag, request constructor/doer hooks, and requested access level. `NewClient`, `NewTestClient`, `SetAccess`, `BugGroups`, `Bug`, `Text`, `query`, and `queryURL` implement API operations. `BugGroupType` bitmasks select open/fixed/invalid groups, and a global ticker throttles unauthenticated public requests.

Control flow: higher-level methods build endpoint paths, call `query`, which calls `Text`, reads the body, checks HTTP status, unmarshals JSON, and reflects on the `Version` field. `Text` adds a bearer token when present or waits on the one-second throttler when not. `queryURL` unescapes HTML links, appends `json=1` and `access`, and resolves against the configured dashboard URL.

State and persistence: client state is in-memory only. The package-level ticker is shared across tokenless clients.

Dependencies and integration: depends on `net/http`, JSON, URL parsing, reflection, and the DTOs from `api.go`. It integrates with dashboard access-level query parameters and OAuth bearer-token support.

Risks: reflection assumes result is a pointer to a struct with integer `Version`; misuse panics. Tokenless calls are globally throttled and can serialize unrelated clients. Error messages include up to 1024 bytes of response body, which is useful but may expose server text in logs.

Test signals: injected constructor/doer via `NewTestClient`, URL query construction, token header behavior, throttling path, HTTP error handling, JSON unmarshal failures, and unsupported version errors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/api/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/access.go -->
# sources/test-tools/syzkaller/dashboard/app/access.go research

Purpose: dashboard authorization and text-asset access control for public, user, and admin visibility levels.

Important APIs, types, and functions: defines `AccessLevel`, `AccessPublic`, `AccessUser`, `AccessAdmin`, `ErrAccess`, `checkAccessLevel`, `isEmailAuthorized`, `currentUser`, `accessLevel`, `userAccessLevel`, `checkTextAccess`, `checkCrashTextAccess`, `checkJobTextAccess`, `Bug.sanitizeAccess`, and `sanitizeReporting`.

Control flow: request access is determined from App Engine user identity or OAuth, trusted auth domain, admin status, ACL entries, and optional `access` downgrade query. Text access dispatches by text tag: job-owned texts query `Job`, crash-owned texts query `Crash` and parent `Bug`, some deduplicated namespace texts are allowed by namespace, and unknown/default text requires admin. Bug access is sanitized by current reporting stage, with fixed/invalid/committed bugs optionally visible at later reporting levels after private reporting fields are stripped.

State and persistence: reads global config, App Engine user context, datastore `Crash`, `Job`, and `Bug` entities. It mutates in-memory bug reporting fields during sanitization but does not persist those sanitized copies.

Dependencies and integration: uses App Engine datastore, logging, user/OAuth APIs, dashboard text tag constants, namespace reporting config, and page/API handlers that call `checkAccessLevel` or `checkTextAccess`.

Risks: access decisions depend on accurate datastore reverse links from text IDs to jobs/crashes. Deduplicated machine/kernel-config style texts rely on namespace checks because exact ownership is not always recoverable. `trustedAuthDomain` is mutable for tests and must remain production-safe.

Test signals: access tests cover config levels, signed-in versus public redirects, forbidden statuses, text URLs by numeric/hex IDs, sanitized hidden references, admin downgrades, ACL email/domain matching, and OAuth/public fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/access.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/access_test.go -->
# sources/test-tools/syzkaller/dashboard/app/access_test.go research

Purpose: comprehensive tests for dashboard access-level assignment, UI/text visibility, reference leakage, and user authorization logic.

Important APIs, types, and functions: `TestAccessConfig`, `TestAccess`, `makeUser`, and `TestUserAccessLevel`. The test uses `NewSpannerCtx`, dashboard clients, bug/crash/build helpers, AI job creation, `AuthGET`, and App Engine login URL checks.

Control flow: `TestAccess` creates fixtures across `access-admin`, `access-user`, and `access-public` namespaces, uploads builds/crashes with access-specific marker strings, transitions bugs through invalid/fixed/open/dup/reporting states, creates AI jobs, records expected entity access levels, then requests each URL at lower access levels and scans replies for forbidden references. `TestUserAccessLevel` table-tests auth-domain, unauthenticated, ACL-authorized, and admin downgrade behavior.

State and persistence: populates test datastore/Spanner state with builds, bugs, crashes, texts, assets, reportings, and AI jobs. All state is test-scoped through the test context.

Dependencies and integration: validates `access.go` plus many handlers that render pages or serve text. It also exercises dashboard config, reporting updates, crash assets, AI job pages, and App Engine user/login behavior.

Risks: the test is intentionally broad and long; failures can originate in rendering or fixture setup rather than the access function itself. Short mode skips many combinations and mainly checks no public access to non-public URLs.

Test signals: expected HTTP OK/redirect/forbidden outcomes, absence of higher-level marker strings in lower-level responses, correct machine-info namespace behavior, and exact `userAccessLevel` table outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/access_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/admin.go -->
# sources/test-tools/syzkaller/dashboard/app/admin.go research

Purpose: administrative and migration handlers for dashboard maintenance, bisection/job repair, datastore cleanup, email sending, bug-field backfills, crash-priority regeneration, and commit-info refresh.

Important APIs, types, and functions: functions include `handleInvalidateBisection`, `dropNamespace`, `dropNamespaceReportingState`, `dropEntities`, `restartFailedBisections`, `updateBugReporting`, `updateCrashPriorities`, `setMissingBugFields`, `adminSendEmail`, `updateHeadReproLevel`, `updateBatch`, and `forceCommitInfoUpdate`.

Control flow: most handlers first require admin access, parse request parameters, query datastore entities, print dry-run or progress output, and apply batched transactional updates through `updateBatch`. Destructive namespace deletion is intentionally disconnected from handlers and defaults to `dryRun := true`. Bisection restart lists failed jobs and only applies when `apply=yes`. Crash-priority/head-repro updates recompute derived fields from existing bugs, crashes, builds, and repro state.

State and persistence: can update or delete datastore entities, reporting state, jobs, bugs, crashes, and text-like entities. Some operations send email or restart bisection jobs. `updateBatch` writes in XG transactions in batches of 20.

Dependencies and integration: depends on App Engine datastore/log/mail, dashboard job/bug/build/crash models, reporting state, text storage, bisection invalidation, and admin HTTP routing where connected.

Risks: several functions are dangerous migrations with comments warning there is no undo. Admin checks are essential for connected handlers, while unconnected helpers rely on `runtime.KeepAlive` to avoid dead-code warnings. Panics inside batch transforms can abort maintenance transactions.

Test signals: admin-only rejection, dry-run output for namespace drops, job error listing without apply, transactional update counts, successful recomputation of repro levels/crash priorities, and no deadcode failures due `runtime.KeepAlive`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/admin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/ai.go -->
# sources/test-tools/syzkaller/dashboard/app/ai.go research

Purpose: dashboard UI and API implementation for AI workflow jobs, including manual job creation, agent polling, job completion, trajectory rendering, access filtering, staged reporting, patch iterations, bug labeling, and Gerrit upload.

Important APIs, types, and functions: UI structs include `uiAIJobsPage`, `ManualWorkflowSpec`, `uiAIJobPage`, `uiAIJob`, `uiJobReporting`, and patch history structs. Major functions include `manualAIWorkflows`, `handleAIJobsPage`, `handleAIJobCreate`, `handleAIJobPage/Post`, `buildAIJobPollArgs`, `apiAIJobPoll`, `pollAIJob`, `apiAIJobDone`, `autoCreateAIJobs`, `autoCreatePatchIterationJobs`, `buildPatchHistory`, `loadPatchLineage`, `collectChangelog`, `aiJobApplyLabels`, `workflowsForBug`, and `createGerritChange`.

Control flow: web handlers list jobs with cursor pagination, filter by workflow/aborted state, enforce namespace access, and render JSON or templates. Manual creation validates AI-action permission and workflow schemas, resolves kernel config input, and creates `aidb.Job` rows. Agent polling records liveness/workflows, prefers stale jobs, then patch iterations, then normal queued/auto-created jobs. Job completion stores results/errors, applies labels, finalizes patch iterations, optionally uploads Gerrit changes, and creates initial staged reportings for successful patching jobs.

State and persistence: persists jobs, reportings, comments, trajectories, journals, labels, bug crash references, pending workflow fields, and generated comments through Spanner (`aidb`) and App Engine datastore/text storage. UI formatting may resolve text blobs into args but does not persist them.

Dependencies and integration: integrates dashboard config, `dashapi`, `aidb`, AI workflow output types, App Engine datastore, templates, lore links, email formatting, Gerrit, VCS links, crash title classification, target metadata, and access control from `access.go`.

Risks: the file coordinates two storage systems and multiple external integrations, so idempotency and transaction boundaries matter. Workflow suffix authorization prevents clients from executing disallowed jobs. Patch-iteration selection is intentionally randomized and capped. Large JSON/result schema changes can break `castJobResults` parsing. Manual actions must not bypass staged-reporting constraints.

Test signals: AI job UI JSON/export, agent poll/done APIs, access filtering, retry/backoff behavior, label application, patch lineage/changelog formation, staged reporting transitions, comment debounce iteration creation, and Gerrit/log error paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/ai.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/ai_report.go -->
# sources/test-tools/syzkaller/dashboard/app/ai_report.go research

Purpose: external AI patch-reporting command and polling API for integrations such as lore-relay.

Important APIs, types, and functions: functions include `apiAIReportCommand`, `handleUpstreamCommand`, `checkActionAuthorized`, `processUpstreamSubcommand`, `determineNextStage`, `handleRejectCommand`, `handleUnrejectCommand`, `handleCommentCommand`, `apiAIPollReport`, `makeNewReportResult`, `populateIterationReportResult`, `apiAIConfirmReport`, `handleCommandError`, and `lookupJobByExtReq`. Constant `SourceWebUI` names manual web-originated commands.

Control flow: command handling first performs idempotency checks by source/ext ID, looks up the reporting/job by root external ID, dispatches upstream/reject/unreject/comment subcommands, and converts expected domain errors into response `Error` strings while logging them for duplicate suppression. Upstream authorization checks optional allowed authors and DKIM, verifies the job is patch-upstreamable, determines the next configured AI stage, and records an upstream command/reporting. Polling scans pending reportings for an integration source, loads jobs and namespace stage config, converts patching or iteration results into `dashapi.ReportPollResult`, merges bug closure/reported-by links, chooses mailing-list recipients, and reports whether a later upstream stage is possible.

State and persistence: reads/writes Spanner `aidb` jobs, reportings, journals, comments, command logs, and published external IDs. Comment bodies are stored in dashboard text storage and referenced as `text://` URIs.

Dependencies and integration: connects `dashapi` external-report endpoints, namespace `AIConfig` stage settings, DKIM/auth metadata, email recipient formatting, lore/message IDs, App Engine text storage, and AI output schemas.

Risks: external commands are security sensitive; allowed-author plus DKIM enforcement is optional by namespace config and must be correct when enabled. Idempotency requires both `Source` and `MessageExtID`. Stage ordering rejects later-stage conflicts, which protects reporting consistency but can surprise operators after config changes.

Test signals: duplicate command no-ops, unauthorized command errors, reject/unreject/upstream state transitions, report-not-found mapping, poll output recipients/CC merging, patch metadata formatting, changelog creation for iterations, comment duplicate suppression, and publish confirmation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/ai_report.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/ai_report_lore_test.go -->
# sources/test-tools/syzkaller/dashboard/app/ai_report_lore_test.go research

Purpose: integration tests for AI report publication and command/comment handling through lore-relay.

Important APIs, types, and functions: tests include `TestAILoreIntegration`, `TestAILoreIntegrationReject`, `TestAILoreUnknownMessageID`, `TestAILoreIntegrationComment`, and `TestAILoreIteration`, plus `integrationMockSender`. They use `NewSpannerCtx`, `lore.NewTestLoreArchive`, `lore.NewPoller`, `lorerelay.NewRelay`, dashboard agent/global clients, and `dashapi` AI requests.

Control flow: tests create AI patch jobs, finish them with patch metadata, poll the dashboard to send moderation/public emails, inject lore archive messages containing `#syz upstream`, `#syz reject`, `#syz unreject`, and plain comments, then poll lore/dashboard again to assert resulting emails, errors, reportings, comments, and iteration jobs. Iteration tests advance fake time past debounce windows, poll an agent for patch-iteration work, complete replies or patch v2/v3, and verify stage/version-specific subjects and inherited sign-off behavior.

State and persistence: uses temporary Git-backed lore archives and Spanner/dashboard test state. `integrationMockSender` captures sent email structs and returns deterministic mock message IDs.

Dependencies and integration: exercises `ai_report.go`, `ai.go` iteration logic, lore polling, lore-relay command parsing, email formatting, trajectory-assisted tags, comment storage, DKIM/own-email flags, and dashboard API clients.

Risks: these are broad integration tests and can fail due behavior changes in email formatting, message threading, fake-time ordering, or lore archive polling. The tests explicitly handle non-deterministic comment ordering when timestamps match.

Test signals: expected email counts/recipients/subjects/bodies, no duplicate error replies after relay restart, silence on unknown message IDs, reject/unreject/upstream failure messages, no iteration for rejected patches, stored comment body/own-email flags, patch-history fixes propagation, and version reset per reporting stage.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/ai_report_lore_test.go -->
