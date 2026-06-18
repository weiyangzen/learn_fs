<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/uv.h -->
# sources/distributed-fs/ceph-client/arch/s390/boot/uv.h

Purpose: Declares the small boot-local ultravisor helper API used by s390 startup and layout code.

Important APIs/types/functions: Declares `adjust_to_uv_max()`, `sanitize_prot_virt_host()`, and `uv_query_info()`.

Control flow: Header only; no runtime control flow.

State and persistence: Header only; persistent state is defined in `uv.c`.

Dependencies and integration points: Included by `startup.c` and `uv.c` to share ultravisor boot declarations without exposing unrelated kernel UV internals.

Risks: Missing declarations here will surface as boot build issues. Signature drift would break early layout and protected-virtualization setup.

Test signals: s390 boot builds with protected virtualization configs and compilation after UV helper signature changes.

Source read size: 9 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/uv.h -->
