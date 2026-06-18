# sources/distributed-fs/ceph-client/include/trace/events/rpm.h

Purpose: Defines runtime power-management tracepoints for suspend/resume/idle/usage operations, integer return values, and status changes.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(rpm_internal)` backs `rpm_suspend`, `rpm_resume`, `rpm_idle`, and `rpm_usage`. `rpm_return_int` records callback return values, and `rpm_status` records status transitions. Symbolic maps decode runtime PM request, event, and status values.

Control flow: Runtime PM core emits internal events when usage counts or requests drive idle/suspend/resume decisions, return events after callbacks, and status events when device runtime state changes.

State and persistence: No state is owned. It observes `struct device` runtime PM fields, usage counts, disable depth, child counts, request type, status, and errors. Runtime PM state is in-memory and device-lifetime scoped.

Dependencies and integration points: Depends on ktime and tracepoints. It integrates with driver core runtime PM, autosuspend, PM domains, bus callbacks, and device drivers.

Risks and test signals: Risks include tracing under PM locks, confusing request/status symbolic maps, callback return interpretation, and high event volume during autosuspend churn. Test runtime PM get/put balance, autosuspend, forbid/allow, supplier/consumer links, system suspend interaction, callback failures, and device unbind while active.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rpm.h` completely for this pass (149 lines, 3427 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rpm.h_research.md`.
