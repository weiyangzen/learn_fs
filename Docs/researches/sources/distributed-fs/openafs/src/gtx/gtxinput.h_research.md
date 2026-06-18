# sources/distributed-fs/openafs/src/gtx/gtxinput.h

Purpose: declares the GTX input server entry point.

Important API: `void *gtx_InputServer(void *)` accepts a generic parameter that is expected to be a `struct gwin *` at runtime. It returns a `void *` so it can be used as a pthread start routine as well as called synchronously.

Control flow and state: this header contains no state, but the implementation reads and mutates the window's attached `gtx_frame`, dispatches keys through the frame keymap, and exits recursive loops via frame flags.

Dependencies and integration: used by `frame.c` for recursive prompts, by `gtxtest.c` for the main event loop, and by `input.c` for pthread startup integration.

Risks: because the parameter is untyped, misuse is only caught at runtime. The current `gtx_Init` implementation can create an input thread with a `NULL` argument, which would be unsafe if that path is used. Test signals should include synchronous calls with a valid window and avoid or fix threaded startup before testing it.
