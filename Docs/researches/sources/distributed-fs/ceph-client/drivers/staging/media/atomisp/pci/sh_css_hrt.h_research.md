# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_hrt.h

Purpose: `sh_css_hrt.h` declares host runtime entry points for controlling and observing SP/ISP execution in the CSS driver. It is a small boundary between higher-level CSS code and lower-level SP/ISP hardware accessors.

Important APIs/types/functions: declarations include `sh_css_hrt_sp_start_si()`, `sh_css_hrt_sp_start_copy_frame()`, `sh_css_hrt_sp_start_isp()`, `sh_css_hrt_sp_wait()`, and `sh_css_hrt_system_is_idle()`. The start functions are implemented elsewhere in the driver, while wait and idle are implemented in `sh_css_hrt.c`.

Control flow and state: the header has no state. Its APIs imply lifecycle flow: configure SP/ISP work, start a specific SP path, optionally wait, then check system idleness.

Dependencies and integration: it includes `sp.h`, `isp.h`, and `ia_css_err.h`. Consumers include stream/pipeline control and diagnostic code that needs SP and ISP identifiers or error conventions.

Risks: exposing multiple start functions without state typing means callers must know which start path matches the current SP program and firmware state. `sh_css_hrt_sp_wait()` is declared as returning an int but currently always returns 0, so callers cannot rely on timeout/error reporting.

Test signals: compile/link tests should ensure all declared start functions have implementations. Integration tests should verify correct sequencing for start, wait, and idle checks across copy frame, sensor input, and ISP execution paths.
