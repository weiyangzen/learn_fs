# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tuning.h

Purpose: Declares the Xe tuning subsystem API for initializing, processing, and dumping GT/engine/LRC tuning state.

Important APIs/types/functions: Declares `xe_tuning_init`, `xe_tuning_process_gt`, `xe_tuning_process_engine`, `xe_tuning_process_lrc`, and `xe_tuning_dump`, with forward declarations for `drm_printer`, `xe_gt`, and `xe_hw_engine`.

Control flow: GT setup calls init and GT processing; engine setup calls engine and LRC processing; diagnostics call dump.

State and persistence behavior: No state in the header. API consumers operate on tuning state stored in GT/HWE structures.

Dependencies and integration points: Included by GT and engine initialization code and any debugfs/diagnostic printer that exposes tuning decisions.

Risks: Callers must initialize tuning bookkeeping before processing tables or dumping active bits. Missing process calls will leave saved-register tuning absent.

Test signals: Build coverage plus platform initialization tests showing tuning dump output after processing.
