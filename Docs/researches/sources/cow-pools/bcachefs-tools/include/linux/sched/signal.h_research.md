# File Research: sources/cow-pools/bcachefs-tools/include/linux/sched/signal.h

Defines `fatal_signal_pending()`, `signal_pending()`, and `signal_pending_state()` as always false. Kernel signal interruption paths compile but do not observe userspace signal state through these helpers.
