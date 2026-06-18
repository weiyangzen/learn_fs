# sources/distributed-fs/orangefs/src/io/job/job-desc-queue.h

Purpose: defines the central `job_desc` structure and job queue API for the OrangeFS asynchronous job layer.

Important APIs/types: descriptor structs hold BMI operation id/error/size, Trove operation state, precreate-pool state, unexpected BMI/dev upcalls, flow pointer/progress timeout state, request scheduler state, and null-job error. `enum job_type` enumerates job categories. `struct job_desc` combines public job id/user/context/status fields, thread-manager callbacks, hints, the operation union, queue links for job and timeout lists, and `time_bucket` backpointer. Queue API prototypes manage allocation and FIFO queues.

State/integration: `job_desc` is the object passed among job APIs, thread-manager callbacks, flow cancellation, and timeout management. `job_time_mgr.c` uses `job_time_link` and `time_bucket`; flow jobs use `u.flow.last_amt_complete` and `timeout_sec`.

Risks/test signals: the union is broad and type-dependent, so every consumer must initialize only the matching fields. Queue and time links make double insertion/removal a risk. Tests should validate each job type initialization path, callback data ownership, timeout linkage, and id-generator behavior.
