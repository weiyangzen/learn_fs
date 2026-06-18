# sources/distributed-fs/ceph-client/arch/sparc/lib/copy_page.S

Purpose: Baseline and Cheetah-patchable SPARC64 page copy implementation.

Important APIs/functions: Exports `copy_user_page` and defines `cheetah_patch_copy_page`.

Control flow: Copies a page using VIS/block load-store paths with prefetch and cache considerations. The Cheetah patch hook modifies specific instructions to tune page-copy behavior for that CPU class.

State and persistence: Page copy mutates destination only; patch hook modifies instruction text.

Dependencies/integration: Includes VIS, thread, page, pgtable, Spitfire, and head headers. May be superseded by NG/NG4/GEN page patchers.

Risks/test signals: Patchable instruction locations and cache aliasing are high risk. Test full page copies, COW/user-page paths, Cheetah patch application, and data integrity across page colors.
