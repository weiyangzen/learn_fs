# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_debugfs.c

## Purpose
This file provides shared MT792x debugfs/seqfile helpers for TX aggregation statistics, hardware/software queue state, and runtime PM statistics/idle timeout controls.

## Important APIs, Types, And Functions
Exports are `mt792x_tx_stats_show()`, `mt792x_queues_acq()`, `mt792x_queues_read()`, `mt792x_pm_stats()`, `mt792x_pm_idle_timeout_set()`, and `mt792x_pm_idle_timeout_get()`. `mt792x_ampdu_stat_read_phy()` is the main internal aggregation-stat printer.

## Control Flow
TX stats take the MT792x mutex, refresh MIB stats, print AMPDU length ranges and BA miss count, then print AMSDU packing histogram. AC queue debug reads PLE empty masks, walks non-empty AC subqueues, selects each queue via `MT_PLE_FL_Q0_CTRL`, and accumulates lengths from `MT_PLE_FL_Q3_CTRL`. Queue read prints mt76 software head/tail/queued counters for data, WM MCU, and FWDL queues. PM stats derive current awake/doze durations from accumulated counters plus current jiffies depending on `MT76_STATE_PM`. Idle timeout setters/getters translate milliseconds to jiffies.

## State And Persistence
The file reads and updates MIB accumulation through shared MAC helpers, reads PLE and queue registers, reports mt76 queue state, and mutates `dev->pm.idle_timeout`. Debugfs changes persist until device removal or another write.

## Dependencies And Integration Points
It depends on `seq_file`, debugfs attribute wiring in chip-specific init code, MT792x register definitions, shared MAC MIB update logic, mt76 queues, and connac PM statistics.

## Risks
Debugfs reads take the device mutex and touch registers, so they must not race with sleep/reset paths. Queue walking assumes PLE register layout and only covers the queues listed. Idle timeout writes can materially alter runtime PM behavior during traffic tests.

## Test Signals
Readable debugfs files during idle and traffic, sane AMPDU/AMSDU counters, queue depth changes under load, PM awake/doze accounting, idle-timeout writes, and no lockdep/reset races validate these helpers.
