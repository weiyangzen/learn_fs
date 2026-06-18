# sources/distributed-fs/ceph-client/include/xen/interface/io/tpmif.h

Purpose: defines version 2 Xen virtual TPM shared-page protocol state and packet layout.

Important APIs/types/functions: `enum vtpm_shared_page_state` with `VTPM_STATE_IDLE`, `SUBMIT`, `FINISH`, and `CANCEL`; `struct vtpm_shared_page` with `length`, `state`, `locality`, `nr_extra_pages`, and flexible `extra_pages` grant IDs.

Control flow: XenBus open requires frontend to publish `ring-ref`, `event-channel`, and `feature-protocol-v2`, then both sides transition to connected after backend maps the grant and verifies protocol support. Frontend submits by filling length/locality/extra pages and changing state to `SUBMIT`; backend processes and moves to `FINISH` or `IDLE`. Frontend can request cancellation with `CANCEL`.

State and persistence: the shared page stores the current request/response lifecycle and optional extra page grants for long packets. Backend should only write `IDLE` or `FINISH`; frontend should only write `SUBMIT` or `CANCEL`.

Dependencies and integration points: integrates with XenBus state machine, event channels, grant table pages, and guest TPM/TIS or vTPM drivers.

Risks: state ownership is strict; either side writing the wrong state can race or lose requests. Long-packet `extra_pages` length is controlled by `nr_extra_pages`, so bounds validation is required. The close sequence must unmap grants and events before backend returns to InitWait.

Test signals: vTPM open/close state transitions, request/response exchange, cancel behavior, long request with extra pages, locality propagation, and invalid state transition handling.
