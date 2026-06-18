# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_timer.c

Purpose: provides a periodic 200 ms QAT firmware time synchronization worker used to trigger firmware heartbeat, rate-limiting, and telemetry timer events on platforms that use this internal sync timer.

Important APIs: `adf_timer_start` and `adf_timer_stop`. Static `work_handler` requeues itself and sends `adf_send_admin_tim_sync`.

Control flow and state: start allocates `struct adf_timer`, stores it in `accel_dev->timer`, records initial real time, initializes delayed work, and queues the first run. Each run requeues for 200 ms, computes elapsed periods from current real time divided by 200 ms, and sends that period count to firmware. Stop cancels delayed work, frees the context, and clears `accel_dev->timer`.

Dependencies and integration: uses misc workqueue, admin timer sync command, ktime, and device lifecycle `hw_data->start_timer/stop_timer`. Heartbeat forces 200 ms timer when this context exists.

Risks and test signals: failure to send sync logs but continues; real-time jumps can affect period count. Test start/stop cycles, shutdown while work pending, admin failure logging, and interaction with heartbeat timer minimum.
