# sources/cloud-native/overlaybd/src/version.h

Purpose: exposes the build-time OverlayBD version string as a C++ constant.

Important APIs/types/functions: macros `MACROTOSTR` and `PRINTMACRO` stringify `OVERLAYBD_VER`; `static const char OVERLAYBD_VERSION[]` stores the expanded version.

Control flow: compile-time macro expansion only.

State and persistence: no runtime state. The compiled binary embeds the version value.

Dependencies/integration: requires the build system to define `OVERLAYBD_VER`; consumers include the header to report version information.

Risks: if `OVERLAYBD_VER` is undefined, the literal string `"OVERLAYBD_VER"` is embedded, which can silently mask build metadata errors.

Test signals: binary version output or compile-time assertions should verify the macro is defined in release builds.
