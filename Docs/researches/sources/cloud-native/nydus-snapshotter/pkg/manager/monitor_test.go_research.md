# Research: sources/cloud-native/nydus-snapshotter/pkg/manager/monitor_test.go

This test file validates the liveness monitor using temporary Unix sockets. `startUnixServer` accepts one connection and keeps it open until its context is canceled. `TestLivenessMonitor` starts two such servers, subscribes daemon IDs, verifies duplicate subscription for the same ID/path errors, runs the monitor, cancels the first server and receives a death event, unsubscribes the second daemon, cancels it, and verifies no extra event is queued. Finally it destroys the monitor and asserts internal maps are empty.

The test gives meaningful coverage of subscription, duplicate detection, epoll HUP delivery, unsubscribe suppression, and cleanup. It uses real Unix sockets and epoll behavior, so it is closer to integration than pure unit testing.

Residual risks include timing sensitivity from sleeps, single-connection server behavior, lack of coverage for failed dial retries, fd control failures, monitor goroutine shutdown after epoll fd close, and manager recovery reactions to delivered death events. Temporary socket files are the only persisted state.
