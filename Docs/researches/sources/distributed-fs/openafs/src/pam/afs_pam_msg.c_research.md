<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_pam_msg.c -->
# sources/distributed-fs/openafs/src/pam/afs_pam_msg.c

## Purpose
Wraps PAM conversation callbacks for displaying informational/error messages and prompting for passwords or other user input using OpenAFS message IDs.

## Important APIs, Types, And Functions
Functions are `pam_afs_printf` and `pam_afs_prompt`. Both call `pam_afs_message`, format varargs into a `PAM_MAX_MSG_SIZE` stack buffer, construct a `struct pam_message`, invoke `pam_conv->conv`, and clean returned `struct pam_response` storage.

## Control Flow
`pam_afs_printf` emits one `PAM_ERROR_MSG` or `PAM_TEXT_INFO` and frees any returned response. `pam_afs_prompt` emits one echo-on or echo-off prompt, returns the response string to the caller, and frees only the response container. Both return `PAM_CONV_ERR` if no valid conversation exists.

## State And Persistence
The helpers store no persistent state. `pam_afs_prompt` transfers ownership of the response string to the caller, which is expected to wipe/free password responses.

## Dependencies And Integration Points
Authentication, setcred, and password-change code use these helpers to prompt consistently through the application-provided PAM conversation.

## Risks And Test Signals
Risks include `vsprintf` into a fixed buffer, no check that the conversation returned a response for prompts, and ownership mistakes around sensitive responses. Test signals include prompt success/failure paths, echo-on/off behavior, oversized formatted messages, and valgrind/ASan checks for response cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_pam_msg.c -->
