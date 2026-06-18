# sources/compression/xz/src/liblzma/common/easy_preset.h

Purpose: internal shared definition for easy preset translation results.

Important APIs/types/functions: defines `lzma_options_easy` with embedded `lzma_options_lzma opt_lzma` and `lzma_filter filters[2]`; declares `bool lzma_easy_preset(lzma_options_easy *easy, uint32_t preset)`.

Control flow: no runtime control flow in the header. The type layout lets `easy_preset.c` create a stack-owned one-filter LZMA2 chain for immediate use by easy APIs.

State and persistence: no global state. Instances hold options and filter pointers that are valid as long as the `lzma_options_easy` object remains alive.

Dependencies/integration: includes `common.h`. Used by easy encoder initialization, single-call buffer encoding, and memory-usage helpers.

Risks: the filter array contains a pointer to `opt_lzma` inside the same structure; copying or using it after the parent object dies is unsafe unless the downstream initializer copies options synchronously. Structure changes require all easy API users to be recompiled.

Test signals: compile coverage in encoder builds and runtime tests that easy APIs do not retain stale stack pointers after initialization.
