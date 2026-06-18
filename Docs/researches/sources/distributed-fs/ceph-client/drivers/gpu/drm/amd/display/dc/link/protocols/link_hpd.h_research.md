# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_hpd.h

Purpose: declares basic HPD helpers for link protocol code.

Important APIs: `get_hpd_line`, `program_hpd_filter`, `dpia_query_hpd_status`, `link_get_hpd_state`, `link_get_hpd_gpio`, `link_enable_hpd`, `link_disable_hpd`, and `link_enable_hpd_filter`.

Control flow/state: this header exposes both encoder-backed HPD operations and BIOS/GPIO discovery helpers. `dpia_query_hpd_status` is declared here for USB4 tunnel HPD integration but is implemented outside this file pair.

Dependencies/integration: includes `link_service.h` for `dc_link`, BIOS, GPIO service, and HPD source types.

Risks: users may assume all declarations are implemented in `link_hpd.c`; DPIA HPD status is separate. Callers must handle `NULL` GPIO returns and unknown HPD source IDs.

Test signals: compile/link coverage for DPIA and non-DPIA HPD users plus connector-type HPD filter behavior.
