# sources/distributed-fs/coda/coda-src/auth2/avenus.h

Purpose: Public declarations for Venus token management helpers.

Important APIs/types: Declares `U_DeleteLocalTokens`, `U_GetLocalTokens`, and `U_SetLocalTokens` over `ClearToken`, `EncryptedSecretToken`, and realm strings.

Control flow and state model: Callers set tokens after authentication, optionally fetch them for verification, or delete them for logout.

Persistence and integration: Integrates auth clients with Venus token state via functions implemented in `avenus.c`.

Risks and test signals: Header does not document ioctl side effects or realm length constraints; callers need to handle negative returns and token-size validation.
