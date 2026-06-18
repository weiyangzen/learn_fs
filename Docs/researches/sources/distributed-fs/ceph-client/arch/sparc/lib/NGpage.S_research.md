# sources/distributed-fs/ceph-client/arch/sparc/lib/NGpage.S

Purpose: Niagara optimized copy-page and clear-page routines plus patch hook.

Important APIs/functions: Defines `NGcopy_user_page`, `NGclear_page`, `NGclear_user_page`, and `niagara_patch_pageops`.

Control flow: `NGcopy_user_page` uses prefetch and optimized chunked copy loops for a full page. `NGclear_page`/`NGclear_user_page` use block-init zero stores over `PAGE_SIZE`. The patcher redirects public page operations to NG routines.

State and persistence: Page operations are stateless; patcher modifies kernel text.

Dependencies/integration: Includes `asm/asi.h` and `asm/page.h`; called through CPU patch selection.

Risks/test signals: Page aliasing, cache behavior, and branch patching are sensitive. Test full-page copy/clear, user-page interfaces, and patched routine targets.
