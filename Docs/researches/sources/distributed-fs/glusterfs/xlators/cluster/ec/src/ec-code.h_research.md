# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code.h

Purpose: public interface for EC code-generation selection, lifecycle, build, release, and byte emission.

Important APIs: `ec_code_detect(xlator_t *xl, const char *def)` selects an optional dynamic generator; `ec_code_create()` binds a GF table to a generator; `ec_code_build_linear()` and `ec_code_build_interleaved()` return executable combination callbacks; `ec_code_release()` frees dynamic functions; `ec_code_error()` and `ec_code_emit()` are backend-facing hooks for reporting generation failures and appending bytes.

Control flow and integration: higher EC method code calls the build functions with coefficient arrays. Architecture backends include this header to receive the builder type and emit bytes, while callers only see function pointers. The header depends on `ec-types.h`, `ec-galois.h`, and Gluster list support.

State behavior: `ec_code_t` owns backend selection, GF metadata, and generated-code spaces; the header hides structure details in `ec-types.h`. No persistent on-disk state is exposed. Risks include lifecycle misuse, especially releasing fallback C symbols or calling generated functions after `ec_code_destroy()`, and ABI mismatch between function pointer typedefs and backend calling conventions. Test signals should pair every successful build with release, exercise both linear and interleaved signatures, and run fallback paths after dynamic errors.
