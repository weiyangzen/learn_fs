<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/error_report.h -->
# sources/distributed-fs/ceph-client/include/trace/events/error_report.h

## Purpose
Declares a generic post-report tracepoint for kernel bug detectors. It lets tooling correlate the end of reports produced by KFENCE, KASAN, and WARN paths with a pseudo-unique report id.

## APIs, Control Flow, and State
The header defines `enum error_detector` with `ERROR_DETECTOR_KFENCE`, `ERROR_DETECTOR_KASAN`, and `ERROR_DETECTOR_WARN`, registers those enum values with `TRACE_DEFINE_ENUM()`, and maps them to strings via `show_error_detector_list()`. The `error_report_template` event class records detector and `unsigned long id`; `error_report_end` instantiates it and is documented as firing after the detector finishes printing the report. There is no persistence outside trace buffers.

## Dependencies, Integration, Risks, and Tests
Depends only on tracepoint infrastructure and callers in debugging subsystems. Integration points are KASAN reports, KFENCE reports, warning emission, and any log consumer that needs a structured marker after verbose text output. Risks include treating the id as globally unique when the comment only promises pseudo-uniqueness, adding new detectors without updating the enum/list pair, and emitting before report text is complete. Test signals include fault-injection reports for each detector, `tracefs` event decoding, enum format validation, and checking report-end ordering against console logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/error_report.h -->
