# sources/distributed-fs/ceph-client/drivers/crypto/caam/blob_gen.c

Purpose: CAAM blob encapsulation/decapsulation helper exported for trusted keys and CAAM blob consumers. It allocates a job ring, validates hardware blob support, builds a CAAM job descriptor for blob protocol operations, maps input/output DMA buffers, submits the job, waits synchronously, and returns the generated or decoded blob data.

Important APIs and functions: `struct caam_blob_priv` wraps a job-ring device; `struct caam_blob_job_result` carries completion and error; `caam_blob_job_done()` translates CAAM status and completes waiters; `check_caam_state()` reads controller mode-of-operation; `caam_process_blob()` performs encap/decap and is exported; `caam_blob_gen_init()` obtains a job ring and checks `blob_present`; `caam_blob_gen_exit()` releases it.

Control flow: caller initializes `caam_blob_priv`, then calls `caam_process_blob(info, encap)`. The function validates key modifier length, computes protocol op and output length, handles protected-key black blob/EKT overhead, allocates a descriptor, DMA maps input and output, warns if using insecure test key mode, appends key modifier, seq in/out pointers, and blob operation, enqueues to CAAM JR, waits for completion on `-EINPROGRESS`, updates `info->output_len`, unmaps DMA, and frees the descriptor.

State and persistence: persistent state is the allocated CAAM job ring in `caam_blob_priv`. Per-call state is descriptor memory, DMA mappings, and completion result. Blob contents are written to caller-provided output buffers.

Dependencies and integration points: includes CAAM descriptor construction, job-ring, error, register, and SoC blob headers; exports symbols to trusted key and CAAM blob users; depends on controller `blob_present` and secure/trusted mode for production key uniqueness.

Risks: decapsulation subtracts `CAAM_BLOB_OVERHEAD` from `input_len`, so short inputs are dangerous unless callers validate; protected-key encap uses bidirectional DMA for input because CAAM writes protected key material back through the input buffer path; descriptor sizing must track appended commands; insecure mode falls back to a test key with only a warning.

Test signals: trusted-key blob KATs, encap/decap round trips for normal and protected keys, invalid key modifier length, short blob input rejection, no-blob hardware returning `-ENODEV`, DMA mapping failure unwinds, and secure-mode warning visibility.
