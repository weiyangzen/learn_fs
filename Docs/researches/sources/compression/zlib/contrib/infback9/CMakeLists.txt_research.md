# sources/compression/zlib/contrib/infback9/CMakeLists.txt

Purpose: adds the deflate64 callback inflater sources to the main zlib shared and static targets.

Important APIs/types/functions: conditionally calls `target_sources()` for `zlib` and `zlibstatic` with `infback9.c`, `inftree9.c`, `infback9.h`, `inffix9.h`, and `inftree9.h`.

Control flow: when `ZLIB_BUILD_SHARED` is true, sources are added privately to the shared target; when `ZLIB_BUILD_STATIC` is true, the same source set is added privately to the static target.

State and persistence: no runtime state. It changes CMake target source membership.

Dependencies/integration: depends on parent zlib target names and build options. The source files depend on zlib internals such as `zutil.h`.

Risks: public header installation/export is not handled here; this is internal contrib integration. Adding these sources to the core library exposes extra symbols if not controlled by visibility settings.

Test signals: build success and any external deflate64 consumers are the main signals; there is no local CTest in this folder.
