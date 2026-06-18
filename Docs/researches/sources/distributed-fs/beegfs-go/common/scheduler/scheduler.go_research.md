# sources/distributed-fs/beegfs-go/common/scheduler/scheduler.go

Purpose: implements a priority-aware token scheduler for work queues, balancing back-pressure, observed throughput, rescheduled work, and priority fairness.

Important APIs/types are constants `DefaultPriority` and `priorityLevels`, options `WithNodeName`, `WithFairness`, `WithAllowedTokensBufferPct`, `WithAverageWindow`, `WithAllowedTokensGrowthRateMax`, `WithAllowedTokensMin`, `PriorityToken`, `Scheduler`, `NewScheduler`, token/reschedule methods, submission-ID helpers, `getNextPriorityFunc`, `geometricRatio`, and `geometricFairnessWeights`.

Control flow: `NewScheduler` configures defaults, computes geometric weights, registers expvar metrics once, seeds per-priority submission IDs, and starts a ticker goroutine. The goroutine periodically estimates completed work using an exponential moving average, accumulates allowed token budget, subtracts current queue usage, distributes tokens by dynamic priority weights, and publishes a `[5]PriorityToken` batch to a buffered channel.

State includes atomic per-priority pending work tokens, total tokens, rescheduled-work counts, next rescheduled times under a mutex, next submission IDs, expvar metrics, and scheduling accumulator state inside the goroutine.

Dependencies are context, expvar, runtime, math, atomics, sync, time, strconv, strings, and zap logging. Integration points are BeeRemote/worker managers that add/remove work tokens and consume priority token batches.

Risks: global expvar registration uses first scheduler's node name only. Submission ID functions assume non-empty 13-character base-36 keys. Token distribution fairness depends on callers completing full `getNextPriorityFunc` cycles. Negative counters are possible if remove calls are unbalanced.

Test signals: scheduler tests cover submission ID mapping, priority rotation, and distribution benchmarks, but not ticker behavior or reschedule timing.
