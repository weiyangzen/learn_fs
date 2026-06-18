## sources/cloud-native/moby/integration-cli/docker_cli_top_test.go

Purpose: validates `docker top` process listing across Linux and Windows paths, including argument handling, nonprivileged containers, Windows core processes, and privileged Linux containers.

Control flow starts long-running containers via `runSleepingContainer` or explicit privileged `docker run`, runs `docker top` once or twice, then checks output. `TestTopMultipleArgs` branches expected behavior by daemon OS: Linux should show a `PID` header for `-o pid`, Windows should reject extra arguments. Windows-specific coverage looks for core process names. Linux privileged coverage is skipped under user namespaces.

State is the process list inside a running container and platform-specific process model. Dependencies include `DockerCLITopSuite`, `cli.Docker`, `icmd`, requirement gates, and platform defaults. Risks are output-format drift, Windows process-name assumptions, and userns restrictions. Test signals are CLI output containing `top` or `busybox.exe`, Windows process names, expected error text, and repeated successful listings.
