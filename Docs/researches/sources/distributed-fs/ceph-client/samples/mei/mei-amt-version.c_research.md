# sources/distributed-fs/ceph-client/samples/mei/mei-amt-version.c

Purpose: user-space sample that connects to Intel AMT over MEI and prints AMT code/BIOS version information.

Important APIs/functions: `struct mei`, `mei_init`, `mei_deinit`, `mei_recv_msg`, `mei_send_msg`, MEI ioctls such as client connect, AMT host interface message structs, `amt_verify_response_header`, `amt_verify_code_versions`, `amt_host_if_call`, and `amt_get_code_versions`.

Control flow: main opens a MEI device, connects to the AMT host interface GUID, builds a code-versions request, sends it, receives a response, verifies command/status/length, and prints BIOS plus firmware component versions.

State and persistence: file descriptor and dynamically allocated response/request buffers during process execution only.

Dependencies and integration: Intel MEI character device, AMT firmware client, kernel MEI UAPI, and endian/packing assumptions in host interface structures.

Risks: device or firmware may be absent, busy, or return partial messages. Header validation is critical to avoid trusting malformed firmware responses. Running may require permissions to access `/dev/mei*`.

Test signals: run on AMT-capable Intel hardware with MEI enabled; verify successful connect and version list output; test error handling on systems without MEI.
