# File Research: sources/block-storage/thin-provisioning-tools/src/report.rs

This file implements the shared reporting, logging, prompting, and progress-monitor abstraction used by thin-provisioning-tools commands.

Key elements:
- `LogLevel` models fatal, error, warning, info, and debug levels. `verbose_args()` adds a hidden `-v` count argument, and `parse_log_level()` maps verbosity count onto `LogLevel`.
- `ReportOutcome` records aggregate success/non-fatal/fatal state. `combine()` preserves the worst outcome seen.
- `Report` wraps a `ReportInner` behind mutexes, making report output safe to share across worker threads via `Arc<Report>`.
- `ReportInner` defines the output surface: titles, subtitles, progress, log messages, stdout-forced output, completion, and interactive prompt input.
- `PBInner` uses `indicatif::ProgressBar`, including suspend/resume around prompt input.
- `SimpleInner` emits to stderr and throttles progress messages to once every five seconds.
- `QuietInner` suppresses output and returns empty prompt input.
- `ProgressMonitor` spawns a background thread that polls a processed-count closure every 500 ms and reports percentage progress.

Interactions:
- Used by `thin/check.rs`, `thin/ls.rs`, `thin/dump.rs`, `thin/repair.rs`, `thin/restore.rs`, migration code, and devtools.
- `Report::to_stdout()` is intentionally separate from normal logging for parseable command output such as `TRANSACTION_ID=...`.

Risks and notes:
- `ProgressMonitor::new()` computes `processed() * 100 / total`; callers must avoid `total == 0`.
- Mutex poisoning uses `unwrap()`, so panics inside report users can cascade.
- `QuietInner::get_prompt_input()` silently returns empty input, which is appropriate only for noninteractive paths.
